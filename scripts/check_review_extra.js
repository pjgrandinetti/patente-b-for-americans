// Continuing past the day's review (20261021d, maintainer, 2026-10-21): once the day's set is done, the exam-date
// box says how many questions are still waiting and offers "Continue the review", which starts a session over the
// next slice of the pool, counted on its own ("Extra review: 0 of N"), not against the day's set.
// Run: node scripts/check_review_extra.js (UILANG=it-IT; SRC= another public_html).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US';
const bank=JSON.parse(fs.readFileSync(root+'/questions.json','utf8')).filter(q=>(q.statements||[]).some(s=>!s.retired));
const live=q=>q.statements.filter(s=>!s.retired);
const key=n=>{const d=new Date(); d.setDate(d.getDate()+n); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
// 31 questions due (missed 3 times, two right since). 20 were reviewed TODAY (rv = today), which is the day's set at
// 20 a day, so 11 are still waiting.
const L={1:{},2:{},3:{}}; const cards=bank.slice(0,31);
cards.forEach((q,i)=>{ const st=live(q)[0]; const full={}; q.statements.forEach(s=>{full[s.number]={seen:1,correct:1,streak:1,given:s.answer};});
  for(const l of [1,2,3]) L[l][q.id]={lastSeen:'2026-09-01T00:00:00.000Z',st:JSON.parse(JSON.stringify(full))};
  L[3][q.id].st[st.number]={seen:5,correct:2,streak:2,miss:3,given:st.answer}; if(i<20) L[3][q.id].st[st.number].rv=key(0); });
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
  w.reviewPerDay=()=>20; w.italianoComplete=()=>true; w.renderDashboard();
  const box=$('exam-date-box');
  ok(w.dailyReviewSet().length===0 && w.dailyReviewPool().length===11,'the day\'s set is done and 11 questions are still waiting');
  ok(/^(done|fatto)$/.test(box.querySelector('[data-row=review] dd').textContent) && box.querySelector('[data-row=waiting] dd').textContent==='11','the review row reads done and the waiting row 11: '+box.textContent.replace(/\s+/g,' ').slice(0,260));
  const more=box.querySelector('[data-ed=more]');
  ok(more && !box.querySelector('[data-ed=review]') && more.classList.contains('btn-secondary'),'it offers Continue the review as a secondary button, and no Start');
  ok($('nav-resume').classList.contains('hidden'),'the nav Begin/Resume stays hidden while no session is open');
  more.click();
  const sess=w.eval('session');
  ok(!$('screen-study').classList.contains('hidden') && sess.buildMode==='daily' && sess.reviewExtra===true && sess.queue.length===11,'Continue opens an extra session of the 11 waiting cards');
  ok(/(Extra review: 0 of 11|Ripasso extra: 0 di 11)/.test($('study-progress-label').textContent),'the header counts the extra session alone: '+$('study-progress-label').textContent);
  const li=w.document.querySelector('#card-statements .statement-item'); li.querySelector(li.dataset.answer==='VERO'?'.btn-vero':'.btn-falso').click();
  ok(/(Extra review: 1 of 11|Ripasso extra: 1 di 11)/.test($('study-progress-label').textContent),'an answer advances it: '+$('study-progress-label').textContent);
  w.updateResumeButton();
  ok(!$('nav-resume').classList.contains('hidden') && /(Resume|Riprendi)/.test($('nav-resume-label').textContent),'the nav offers Resume for the extra session');
  ok(w.reviewDoneToday()===21,'the answer counts for the day: 21 done today');
  // Leave, and continue again: the extra session picks up where it was (20261023p), not a fresh block at zero.
  w.showScreen('dashboard'); w.eval('session.buildMode = null'); w.renderDashboard();
  $('exam-date-box').querySelector('[data-ed=more]').click();
  const s2=w.eval('session');
  ok(s2.reviewExtra===true && s2.queue.length===10 && s2.reviewDoneBefore===1 && /(Extra review: 1 of 11|Ripasso extra: 1 di 11)/.test($('study-progress-label').textContent),'continuing again resumes the extra session at 1 of 11 with the 10 cards left: '+$('study-progress-label').textContent);
  // The exam day keeps Continue the review and the waiting count (20261029y); the day before does not.
  w.showScreen('dashboard'); w.eval('session.buildMode = null');
  w.localStorage.setItem('patente_exam_date',key(0)); w.renderDashboard();
  { const b=$('exam-date-box'); ok(!!b.querySelector('[data-ed=more]') && !!b.querySelector('[data-row=waiting]'),'on the exam day the review can be continued, with the waiting count'); }
  w.localStorage.setItem('patente_exam_date',key(1)); w.renderDashboard();
  { const b=$('exam-date-box'); ok(!b.querySelector('[data-ed=more]') && !b.querySelector('[data-row=waiting]'),'the day before stops at the day\'s set'); }
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
