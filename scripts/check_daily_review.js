// The daily review while waiting for the exam (maintainer, 2026-10-03): with an exam date entered, the dashboard sets 20 questions a day, open weak spots first and then the questions missed most in Italian; a question counts at most one correct answer a day and leaves after correct answers on three different days (successive relearning). Run: node scripts/check_daily_review.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US', IT=LANG.startsWith('it');
const bank=JSON.parse(fs.readFileSync(root+'/questions.json','utf8')).filter(q=>(q.statements||[]).some(s=>!s.retired));
const live=q=>q.statements.filter(s=>!s.retired);
const key=n=>{const d=new Date(); d.setDate(d.getDate()+n); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
// 30 statements on 30 cards missed 3 times at Italiano and since answered right twice (not weak spots, still on the list);
// one more (W) missed once with no correct answer since: an open weak spot; one (F) fixed the old way, streak 3.
const L={1:{},2:{},3:{}}; const cards=bank.slice(0,32);
cards.forEach((q,i)=>{ const st=live(q)[0]; const full={}; q.statements.forEach(s=>{full[s.number]={seen:1,correct:1,streak:1,given:s.answer};});
  for(const l of [1,2,3]) L[l][q.id]={lastSeen:'2026-09-01T00:00:00.000Z',st:JSON.parse(JSON.stringify(full))};
  if(i<30) L[3][q.id].st[st.number]={seen:5+(i%3),correct:2,streak:2,miss:3+(i%3),given:st.answer};
  else if(i===30) L[3][q.id].st[st.number]={seen:2,correct:1,streak:0,miss:1};
  else L[3][q.id].st[st.number]={seen:6,correct:3,streak:3,miss:3,given:st.answer}; });
const W=cards[30], F=cards[31];
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.localStorage.setItem('patente_level','3'); for (const l of [1,2,3]) w.localStorage.setItem('patente_progress_L'+l, JSON.stringify(L[l]));
w.localStorage.setItem('patente_exam_date',key(9));
const good=[1,0,1,1,0,2,1,0,1,1,0,1,1,0,1];
w.localStorage.setItem('patente_exam_history',JSON.stringify(good.map((x,i)=>{const d=new Date(); d.setDate(d.getDate()-1-i); return {date:d.toISOString(),correct:30-x,total:30,wrong:x,pass:true,level:3,items:[]};})));
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollTo=function(){}; w.Element.prototype.scrollIntoView=function(){}; w.alert=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const $=id=>w.document.getElementById(id);
setTimeout(()=>{
  // The size of the day's set: forty minutes at the learner's own doubled time per question (20261010f).
  { const d0=w.drillSecondsPerAnswer;
    w.drillSecondsPerAnswer=()=>60; ok(w.reviewPerDay()===40,'at one minute a question: 40 a day');
    w.drillSecondsPerAnswer=()=>68; ok(w.reviewPerDay()===35,'at 68 seconds: 35 (rounded down to a five)');
    w.drillSecondsPerAnswer=()=>600; ok(w.reviewPerDay()===10,'never under 10');
    w.drillSecondsPerAnswer=()=>5; ok(w.reviewPerDay()===50,'never over 50 (20261021a)');
    w.drillSecondsPerAnswer=()=>40; ok(w.reviewPerDay()===50,'at 40 seconds, 60 would fit the forty minutes but the ceiling holds at 50');
    w.drillSecondsPerAnswer=d0; }
  w.reviewPerDay=()=>20;
  w.italianoComplete=()=>true; w.renderDashboard();
  // Today's review count comes from the records' rv stamps (20261011d), not a device tally.
  const stamp=(k,day)=>w.eval(`(()=>{let i=0; for (const c of Object.values(progress)) for (const r of Object.values(c.st||{})) { if (i<${k} && r.miss) { r.rv=${JSON.stringify(day)}; i++; } else delete r.rv; } saveProgress();})()`);
  const unstamp=()=>w.eval('for (const c of Object.values(progress)) for (const r of Object.values(c.st||{})) { delete r.rv; if (r.dd===dayKey()) delete r.dd; } saveProgress()');
  const box=$('exam-date-box');
  const pool=w.dailyReviewPool(), set=w.dailyReviewSet();
  ok(pool.length===31 && set.length===20,'31 questions are due (30 on the list and the weak spot), 20 are set for today');
  ok(set[0].id===W.id,'the open weak spot comes first');
  ok(!pool.some(x=>x.id===F.id),'a question fixed before the change (three in a row) is not brought back');
  ok(set.slice(1).every((x,i,a)=>i===0||a[i-1].total>=x.total),'then the most-missed first');
  ok(/^(20 left|20 da fare)$/.test(box.querySelector('[data-row=review] dd').textContent) && box.querySelector('[data-ed=review]') && /(on 3 different days|in 3 giorni diversi)/.test(box.textContent),'the box names the 20 and the three-day rule, with a start button: '+box.textContent.slice(-150));
  ok($('weak-spots').classList.contains('hidden'),'the weak-spots card is gone: they are in the review');
  box.querySelector('[data-ed=review]').click();
  const sess=w.eval('session');
  ok(!$('screen-study').classList.contains('hidden') && sess.buildMode==='daily' && sess.queue.length===20 && sess.totalQuestions===20,'it opens as study cards: 20 cards, one question each');
  ok(w.document.querySelectorAll('#card-statements .statement-item').length===1,'a card shows only its review question');
  ok(/(Today’s review: 0 of 20|Ripasso di oggi: 0 di 20)/.test($('study-progress-label').textContent),'the header counts the review: '+$('study-progress-label').textContent);
  // answer the first right, the second wrong
  const answer=(right)=>{ const li=w.document.querySelector('#card-statements .statement-item'); const b=li.querySelector(li.dataset.answer==='VERO' ? (right?'.btn-vero':'.btn-falso') : (right?'.btn-falso':'.btn-vero')); const id=sess.queue[sess.index], num=li.dataset.number||b.dataset.number; b.click(); return {id,num}; };
  const a1=answer(true); const r1=w.eval('progress')[a1.id].st[a1.num];
  { const li=w.document.querySelector('#card-statements .statement-item');
    const box=li.querySelector('.stmt-expl-box');
    ok(box && !box.classList.contains('hidden'),'in the review a correct answer opens its explanation (20261011e)');
    ok(IT ? !li.querySelector('.stmt-english-expl') : !!li.querySelector('.stmt-english-expl:not(.hidden)'),'and, for a non-Italian browser, its English'); }
  ok(r1.dr===r1.streak && r1.dr>=1 && r1.dd===key(0),'a correct answer today counts one day, on top of the run the record already had: '+JSON.stringify({dr:r1.dr,dd:r1.dd}));
  const dr0=r1.dr;
  $('btn-next').click(); const a2=answer(false); const r2=w.eval('progress')[a2.id].st[a2.num];
  ok(r2.dr===0 && r2.dd===key(0),'a wrong answer starts the count over');
  ok(w.reviewDoneToday()===2 && w.dailyReviewSet().length===18 && !w.dailyReviewSet().some(x=>(x.id===a1.id&&x.num===a1.num)||(x.id===a2.id&&x.num===a2.num)),'two done: 18 left today, and neither comes back today');
  { // Leaving and starting the review again keeps the day's progress on the bar (20261011g).
    w.showScreen('dashboard'); w.startDailyReview();
    const lab=$('study-progress-label').textContent, c=w.studyCardCounts();
    ok(c.total===20 && c.cleared===2 && /(2 of 20|2 di 20)/.test(lab),'started again: the bar counts the whole day, 2 of 20: '+lab); }
  // a second correct answer the same day adds nothing
  w.noteDayRun(r1,true); ok(r1.dr===dr0,'a second correct answer on the same day adds nothing');
  // later days
  r1.dr=1; r1.dd=key(-1); w.noteDayRun(r1,true); r1.dd=key(-1); w.noteDayRun(r1,true);
  ok(r1.dr===3 && w.dayRunDone(r1,3),'correct on three different days: released');
  w.eval('saveProgress()');
  ok(!w.dailyReviewPool().some(x=>x.id===a1.id&&x.num===a1.num),'and it is no longer due');
  { const three={seen:9,correct:6,streak:3,miss:3,dr:1,dd:key(0)}; ok(!w.dayRunDone(three,3),'three in a row given in one day do not release it'); }
  // The nav's Begin/Resume belongs to the review in this phase (20261010u).
  { const nav=$('nav-resume'), lab=$('nav-resume-label');
    w.document.querySelector('.nav-btn[data-screen="vocab"]')?.click();
    w.updateResumeButton();
    ok(!nav.classList.contains('hidden') && /(Resume|Riprendi)/.test(lab.textContent) && /(today’s review|ripasso di oggi)/.test(nav.title),'away from the review mid-way: the nav button reads Resume, for today\'s review: '+nav.title);
    const at=sess.queue[sess.index];
    nav.click();
    ok(!$('screen-study').classList.contains('hidden') && w.eval('session').buildMode==='daily' && w.studyCardCounts().total===20 && w.document.querySelectorAll('#card-statements .statement-item').length>=1 && !/drill/.test(w.eval('session').buildMode),'it goes back into the review, not the weak-spots drill');
    ok(w.document.querySelectorAll('#card-statements .statement-item').length===1,'and the card is still narrowed to its review question'); }
  // finishing the pass
  w.finishStudyPass(); ok(!$('screen-dashboard').classList.contains('hidden'),'Finish returns to the dashboard');
  // The review setting: off folds a correct answer again; its Settings row shows only in the review phase.
  { w.setReviewExplainOn(false); w.showScreen('dashboard'); w.eval("for (const c of Object.values(progress)) for (const r of Object.values(c.st||{})) delete r.rv"); w.localStorage.setItem('patente_review_day','');
    w.startDailyReview(); const li=w.document.querySelector('#card-statements .statement-item');
    li.querySelector(li.dataset.answer==='VERO'?'.btn-vero':'.btn-falso').click();
    ok(li.querySelector('.stmt-expl-box').classList.contains('hidden'),'with the review setting off, a correct answer stays folded behind Why?');
    w.setReviewExplainOn(true);
    ok(w.buildProgressBundle().settings.reviewExpl==='1','the setting syncs');
    w.syncSettings(); const row=w.document.getElementById('set-review-expl')?.closest('label');
    const grp=()=>w.document.getElementById('set-review-expl').closest('.settings-group');
    ok(row && !grp().classList.contains('hidden') && w.document.getElementById('set-review-expl').checked,'its Settings group shows in the review phase, the row on');
    w.localStorage.removeItem('patente_exam_date'); w.syncSettings();
    ok(grp().classList.contains('hidden'),'and the group is hidden with no exam date');
    w.localStorage.setItem('patente_exam_date',key(9)); w.showScreen('dashboard'); }
  // the merge
  const m=w.mergeCardRecord({st:{1:{seen:3,correct:2,streak:1,dr:2,dd:key(-1)}}},{st:{1:{seen:4,correct:2,streak:0,dr:0,dd:key(0)}}}).st[1];
  ok(m.dr===0 && m.dd===key(0),'a merge takes the later day\'s count, so a miss on another device stands');
  // The Statistics page's controls do not shrink the review (20261010e).
  { const n0=w.dailyReviewPool().length; w.localStorage.setItem('patente_miss_min','6'); w.localStorage.setItem('patente_miss_run','5'); ok(w.dailyReviewPool().length===n0 && w.reviewDaysNeeded()===3,'"Missed at least 6 times" and "leave after 5" on Statistics leave the review as it was: '+n0); w.localStorage.removeItem('patente_miss_min'); w.localStorage.removeItem('patente_miss_run'); }
  // quota used up
  stamp(20,key(0)); w.renderDashboard();
  ok(/^(done|fatto)$/.test(box.querySelector('[data-row=review] dd').textContent) && !box.querySelector('[data-ed=review]'),'twenty answered: today\'s review is done, no button');
  stamp(20,key(-1)); ok(w.dailyReviewSet().length>0,'yesterday\'s count does not carry over');
  { unstamp(); w.eval("session.buildMode='topic'; session.drillStmts=null"); w.showScreen('dashboard'); w.updateResumeButton();
    ok(/(Begin|Inizia)/.test($('nav-resume-label').textContent) && /(Begin today’s review|Inizia il ripasso di oggi)/.test($('nav-resume').title),'nothing reviewed yet today: the nav button reads Begin, for today\'s review');
    $('nav-resume').click(); ok(w.eval('session').buildMode==='daily','and it starts the review');
    w.showScreen('dashboard');
    stamp(20,key(0)); w.eval("session.buildMode='topic'; session.drillStmts=null"); w.updateResumeButton();
    ok($('nav-resume').classList.contains('hidden'),'today\'s review done: the button goes, and does not offer the weak-spots drill');
    unstamp(); }
  // without a date, nothing changes
  w.localStorage.removeItem('patente_exam_date'); w.renderDashboard();
  ok(!$('weak-spots').classList.contains('hidden') && !box.querySelector('[data-ed=review]'),'with no exam date the weak-spots card is back and no review is offered');
  w.updateResumeButton(); ok(!/(today’s review|ripasso di oggi)/.test($('nav-resume').title),'and the nav button no longer belongs to the review: '+$('nav-resume').title);
  ok(IT ? !/review|Start/.test(box.textContent) : true,'in the reader\'s language');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
