// "Questions you keep missing" on the Statistics page (maintainer, 2026-10-01): one list of every question missed at least N times across the levels (N on the page, default 3, synced), most misses first, each row with its figure and misses by level; opened, the English, the answer behind a button and the 📖. The old 25-topic breakdown and the language-miss group are gone. Run: node scripts/check_keep_missing.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US'; const IT=LANG.startsWith('it');
const Q=JSON.parse(fs.readFileSync(root+'/questions.json','utf8')).filter(c=>c.statements.some(s=>!s.retired));
const live=c=>c.statements.filter(s=>!s.retired);
const A=Q.find(c=>c.image)||Q[0], B=Q[5], C=Q[9], D=Q[13];
const a=live(A)[0], b=live(B)[0], c=live(C)[0], d=live(D)[0];
// a: 2+0+3 = 5 (IT face: 3); b: 1+1+1 = 3 (IT face: 1); c: 0+0+2 = 2
const rec=m=>({seen:m+1,correct:1,streak:1,miss:m});
const L={1:{},2:{},3:{}};
const put=(lvl,card,num,m)=>{ if(!m) return; (L[lvl][card.id] ||= {st:{}}).st[num]=rec(m); };
put(1,A,a.number,2); put(3,A,a.number,3); put(1,B,b.number,1); put(2,B,b.number,1); put(3,B,b.number,1); put(3,C,c.number,2); put(1,D,d.number,3);   // d: English only, 3
(L[1][C.id] ||= {st:{}}).st[c.number]={seen:1,correct:1,streak:1};   // c answered right in English
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.localStorage.setItem('patente_level','3');
for (const l of [1,2,3]) w.localStorage.setItem('patente_progress_L'+l, JSON.stringify(L[l]));
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollTo=function(){}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(cnd,m)=>{console.log((cnd?'ok  ':'FAIL')+' '+m); if(!cnd)fails++;};
const $=id=>w.document.getElementById(id);
setTimeout(()=>{
  w.document.querySelector('.nav-btn[data-screen="exam"]').click();
  const box=$('exam-weak'); const rows=()=>[...box.querySelectorAll('details.km-row')];
  const disc=()=>box.querySelector('details.stats-box');
  ok(box && !box.classList.contains('hidden') && disc().querySelector('summary').textContent===(IT?'Domande che continui a sbagliare':'Questions you keep missing'),'the section is there, a disclosure titled');
  ok(!disc().open,'closed by default');
  disc().open=true; disc().dispatchEvent(new w.Event('toggle'));
  ok(!/Right in English|Corrette in inglese|Missed in English and|weak-topic/.test(box.innerHTML),'the old diagnosis and topic breakdown are gone');
  ok($('km-min').value==='3','threshold defaults to 3');
  const r0=rows();
  ok(IT ? r0.length===1 : r0.length===2,'rows at 3, Italian misses only (d, missed only in English, is not listed): '+r0.length);
  ok(r0[0].querySelector('.km-it').textContent===a.italian_text,'most misses first');
  ok(!A.image || !!r0[0].querySelector('img.km-img'),'the figure is in the row');
  const lv=[...r0[0].querySelectorAll('.km-lvl')].map(x=>x.textContent);
  ok(IT ? lv.length===1 && / 3$/.test(lv[0]) : lv.length===3 && / 2$/.test(lv[0]) && / 0$/.test(lv[1]) && / 3$/.test(lv[2]),'misses by level: '+lv.join(' | '));
  ok(r0[0].querySelector('.km-ans').classList.contains('hidden'),'answer, English and explanation are hidden until the question is answered');
  r0[0].open=true; r0[0].dispatchEvent(new w.Event('toggle'));
  ok(!A.image || /\S/.test(r0[0].querySelector('.km-figure img')?.getAttribute('src')||''),'opening the row loads the figure at full size');
  ok(r0[0].querySelectorAll('.km-vf').length===2,'VERO and FALSO buttons');
  ok(IT ? !r0[0].querySelector('.km-en') : r0[0].querySelector('.km-en')?.textContent===a.english_translation,IT?'no English for an Italian browser':'the English is in the opened row');
  const rec3=()=>w.eval(`loadProgressForLevel(3)[${JSON.stringify(String(A.id))}].st[${JSON.stringify(String(a.number))}]`);
  const s0=rec3().streak, seen0=rec3().seen;
  r0[0].querySelector(`.km-vf[data-choice="${a.answer}"]`).click();
  ok(!r0[0].querySelector('.km-ans').classList.contains('hidden') && /Right|Giusto/.test(r0[0].querySelector('.km-answer').textContent) && r0[0].querySelector('.km-answer').textContent.includes(a.answer),'a right answer shows the result: '+r0[0].querySelector('.km-answer').textContent);
  ok(rec3().streak===s0+1 && rec3().seen===seen0+1,'and counts at Italiano: the run grows');
  ok([...r0[0].querySelectorAll('.km-vf')].every(b=>b.disabled),'one answer per opening');
  r0[0].querySelector('.km-book').click();
  ok(!$('review-overlay').classList.contains('hidden'),'📖 opens the notes');
  $('review-overlay').classList.add('hidden');
  const sel=$('km-min'); sel.value='2'; sel.dispatchEvent(new w.Event('change',{bubbles:true}));
  ok(disc().open,'it stays open when a control redraws the list');
  ok(rows().length===(IT?2:3) && w.localStorage.getItem('patente_miss_min')==='2' && w.buildProgressBundle().settings.missMin==='2','threshold 2: more rows, stored and synced');
  if (IT) ok(!$('km-filter'),'no English/Italian filter for an Italian browser');
  else {
    ok($('km-filter').value==='it' && $('km-filter').options.length===3,'three choices, default missed in Italian');
    ok(/language of the exam|lingua dell/.test(box.querySelector('.km-hint').textContent),'a line says what the list is for');
    const want={lang:1,rule:2,it:3};   // c right in English; a and b missed in both
    for (const f of ['lang','rule','it']) {
      const fs_=$('km-filter'); fs_.value=f; fs_.dispatchEvent(new w.Event('change',{bubbles:true}));
      ok(rows().length===want[f],'filter '+f+': '+rows().length+' rows');
    }
    const fs2=$('km-filter'); fs2.value='rule'; fs2.dispatchEvent(new w.Event('change',{bubbles:true}));
    ok(w.localStorage.getItem('patente_miss_filter')==='rule' && w.buildProgressBundle().settings.missFilter==='rule' && /rule|regola/.test(box.querySelector('.km-hint').textContent),'the filter is stored and synced, and its line changes');
    w.localStorage.setItem('patente_miss_filter','both'); ok(w.missFilter()==='rule','a value stored by the previous build maps across');
    const fs3=$('km-filter'); fs3.value='it'; fs3.dispatchEvent(new w.Event('change',{bubbles:true}));
  }
  // The run that takes a question off the list is the learner's choice, default 3 in a row at Italiano.
  const before=rows().length;
  const setStreak=n=>{ w.eval(`(()=>{const p=loadProgressForLevel(3); p[${JSON.stringify(String(A.id))}].st[${JSON.stringify(String(a.number))}].streak=${n}; p[${JSON.stringify(String(A.id))}].st[${JSON.stringify(String(a.number))}].dr=${n};})()`); w.renderMissBreakdown(); };  // the run counts DAYS since 20261010c
  const listed=()=>rows().some(r=>r.querySelector('.km-it').textContent===a.italian_text);
  ok($('km-run').value==='3' && $('km-run').options.length===5,'run choice: five options, default 3 in a row');
  setStreak(2); ok(listed(),'default 3: two in a row is not enough');
  setStreak(3); ok(!listed() && rows().length===before-1,'default 3: three in a row takes it off');
  ok(/answered correctly|risposte correttamente|risposta correttamente/.test(box.querySelector('.weak-note').textContent),'the line says how many are fixed and not listed');
  const pick=v=>{ const el=$('km-run'); el.value=v; el.dispatchEvent(new w.Event('change',{bubbles:true})); };
  pick('2'); setStreak(2); ok(!listed(),'choice 2: two in a row takes it off');
  pick('ws'); setStreak(1); ok(listed(),'weak spots rule: one answer after an Italiano miss is not enough');
  setStreak(2); ok(!listed(),'weak spots rule: two takes it off');
  { pick('3'); w.eval(`(()=>{const r=loadProgressForLevel(3)[${JSON.stringify(String(A.id))}].st[${JSON.stringify(String(a.number))}]; r.streak=3; r.dr=1;})()`); w.renderMissBreakdown(); ok(listed(),'three in a row given on one day do not take it off (20261010c)'); pick('ws'); }
  ok(w.localStorage.getItem('patente_miss_run')==='ws' && w.buildProgressBundle().settings.missRun==='ws','the run choice is stored and synced');
  pick('3');
  // Fixed again, then a mock miss: back on the list.
  w.eval(`(()=>{const p=loadProgressForLevel(3); p[${JSON.stringify(String(A.id))}].st[${JSON.stringify(String(a.number))}].streak=3; p[${JSON.stringify(String(A.id))}].st[${JSON.stringify(String(a.number))}].dr=3;})()`);
  w.renderMissBreakdown();
  ok(rows().length===before-1,'a run of three days: off the list');
  w.eval(`(()=>{const q=questions.find(x=>String(x.id)===${JSON.stringify(String(A.id))}); const st=q.statements.find(x=>String(x.number)===${JSON.stringify(String(a.number))});
    examState.items=[{q,stmt:st}]; examState.answers=[{chosen: st.answer==='VERO'?'FALSO':'VERO', correct: st.answer}]; recordExamMisses();})()`);
  w.renderMissBreakdown();
  ok(rows().length===before && rows()[0].querySelector('.km-it').textContent===a.italian_text,'one wrong answer in a mock exam: back on the list, at the top');
  const sel6=$('km-min'); sel6.value='6'; sel6.dispatchEvent(new w.Event('change',{bubbles:true}));
  // After the mock miss the first question has 6 misses in the English face (2+0+4) and 4 at Italiano.
  ok(rows().length===(IT?0:1) && /6/.test(box.querySelector('.weak-note').textContent),'threshold 6: '+(IT?'none, and it says so':'only the question missed six times'));
  // A wrong answer in the list counts a miss and resets the run.
  w.localStorage.setItem('patente_miss_min','1'); w.localStorage.setItem('patente_miss_run','5'); w.renderMissBreakdown();
  const rr=rows().find(r=>r.querySelector('.km-it').textContent===a.italian_text);
  rr.open=true; rr.dispatchEvent(new w.Event('toggle'));
  const m0=rec3().miss;
  rr.querySelector(`.km-vf[data-choice="${a.answer==='VERO'?'FALSO':'VERO'}"]`).click();
  ok(rec3().streak===0 && rec3().miss===m0+1 && /Wrong|Sbagliato/.test(rr.querySelector('.km-answer').textContent),'a wrong answer counts a miss and resets the run');
  // Read with answers (20261029p): each question in Italian (and English) with its answer, nothing to answer, nothing recorded.
  const n0=rows().length; const rec0=JSON.stringify(rec3());
  ok(!!box.querySelector('.km-mode-btn[data-mode=practice].active') && box.querySelector('.km-mode-btn[data-mode=read]'),'the list opens on Answer them, with Read with answers beside it');
  box.querySelector('.km-mode-btn[data-mode=read]').click();
  const reads=[...box.querySelectorAll('.km-row.km-read')];
  ok(reads.length===n0 && !box.querySelector('details.km-row') && !box.querySelector('.km-vf'),'read mode lists the same questions with no V/F to press: '+reads.length);
  const rd0=reads.find(r=>r.querySelector('.km-it').textContent===a.italian_text);
  ok(rd0 && rd0.querySelector('.km-key').textContent===a.answer,'each question shows its answer');
  ok(IT ? !rd0.querySelector('.km-en') : rd0.querySelector('.km-en').textContent===a.english_translation,IT?'an Italian browser gets no English':'and its English');
  const why=rd0.querySelector('details.km-why');
  ok(why && !why.open && why.querySelector('.km-expl') && (IT ? !why.querySelector('.km-expl-en') : !!why.querySelector('.km-expl-en')),'with its explanation'+(IT?' in Italian':', Italian and English')+', folded under Why?');
  ok(JSON.stringify(rec3())===rec0,'reading records nothing');
  box.querySelector('.km-mode-btn[data-mode=practice]').click();
  ok(rows().length===n0 && !!box.querySelector('.km-vf'),'Answer them brings back the practice rows');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
