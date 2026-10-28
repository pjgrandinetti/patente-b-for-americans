// "Questions you keep missing" on the Statistics page. Since 20261029v (maintainer, 2026-10-29): no menus; the KM_MAX (20) questions the learner is most likely to miss next time, ranked by (misses + 1) / (answers + 2) over the answers in Italian, among those missed in Italian and not yet right on 3 different days; Answer them or Read with answers. Run: node scripts/check_keep_missing.js (UILANG=it-IT).
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
// e: six misses in twenty answers at Italiano, a low rate despite the count
const E=Q[17], e=live(E)[0]; (L[3][E.id] ||= {st:{}}).st[e.number]={seen:20,correct:14,streak:0,miss:6};
// Chances in both faces: a (3+1)/(4+2) .67, c (2+1)/(3+2) .60, b .50 (English face: L2 and L3, 2 of 4; Italian face: L3, 1 of 2), e (6+1)/(20+2) .32.
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
  ok(!$('km-min') && !$('km-filter') && !$('km-run') && !box.querySelector('select'),'no menus (20261029v)');
  const r0=rows();
  const order=r0.map(r=>r.querySelector('.km-it').textContent);
  ok(r0.length===4 && order[0]===a.italian_text && order[1]===c.italian_text && order[2]===b.italian_text && order[3]===e.italian_text,'ranked by the chance of a miss, not by the count: a, c, b, then e with six misses');
  ok(!order.includes(d.italian_text),'a question missed only in English is not listed');
  ok(/(most likely to miss|più probabilità di sbagliare)/.test(box.querySelector('.weak-note').textContent) && /\b3\b/.test(box.querySelector('.weak-note').textContent),'one line says what the list is and when a question leaves it: '+box.querySelector('.weak-note').textContent);
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
  ok([...r0[0].querySelectorAll('.km-vf')].every(bt=>bt.disabled),'one answer per opening');
  ok(!r0[0].querySelector('.km-book'),'no Concepts button on a practice row (20261029u)');
  w.renderMissBreakdown();
  ok(disc().open,'it stays open when the list is redrawn');
  // Leaves after correct answers on 3 different days, the daily review's test.
  const setRun=n=>{ w.eval(`(()=>{const r=loadProgressForLevel(3)[${JSON.stringify(String(A.id))}].st[${JSON.stringify(String(a.number))}]; r.streak=${n}; r.dr=${n};})()`); w.renderMissBreakdown(); };
  const listed=()=>rows().some(r=>r.querySelector('.km-it').textContent===a.italian_text);
  setRun(2); ok(listed(),'right on two different days: still listed');
  setRun(3); ok(!listed() && rows().length===3,'right on three different days: off the list');
  { w.eval(`(()=>{const r=loadProgressForLevel(3)[${JSON.stringify(String(A.id))}].st[${JSON.stringify(String(a.number))}]; r.streak=3; r.dr=1;})()`); w.renderMissBreakdown(); ok(listed(),'three right on one day do not take it off'); setRun(3); }
  w.eval(`(()=>{const q=questions.find(x=>String(x.id)===${JSON.stringify(String(A.id))}); const st=q.statements.find(x=>String(x.number)===${JSON.stringify(String(a.number))});
    examState.items=[{q,stmt:st}]; examState.answers=[{chosen: st.answer==='VERO'?'FALSO':'VERO', correct: st.answer}]; recordExamMisses();})()`);
  w.renderMissBreakdown();
  ok(listed(),'one wrong answer in a mock exam: back on the list');
  // At most twenty.
  w.eval(`(()=>{const p=loadProgressForLevel(3); let k=0; for (const q of questions.slice(40,80)) { const st=(q.statements||[])[0]; if(!st||st.retired) continue; (p[q.id] ||= {lastSeen:null, st:{}}).st ||= {}; p[q.id].st[st.number]={seen:2,correct:1,streak:0,miss:1}; if(++k>=25) break; } saveProgressForLevel(3,p);})()`);
  if (w.eval('currentLevel')===3) w.eval('progress = loadProgressForLevel(3)');
  w.renderMissBreakdown();
  ok(rows().length===20 && /\b20\b/.test(box.querySelector('.weak-note').textContent),'never more than twenty: '+rows().length);
  // A wrong answer in the list counts a miss and resets the run.
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
  ok(!box.querySelector('.km-read .km-book'),'no Concepts button in read mode (20261029t)');
  const why=rd0.querySelector('details.km-why');
  ok(why && !why.open && why.querySelector('.km-expl'),'with its explanation, folded under Why?');
  if (IT) ok(!why.querySelector('.km-expl-en') && !why.querySelector('.rb-it'),'an Italian browser: the Italian explanation, no English, no pill');
  else {
    const pill=why.querySelector('.km-expl-en .rb-it'), itx=why.querySelector('.km-expl-en .rb-itxt');
    ok(why.querySelectorAll('.km-expl').length===1 && why.querySelector('.km-expl-en') && pill && itx && itx.classList.contains('hidden'),'a non-Italian browser: the English explanation only, the Italian behind an IT pill');
    pill.click();
    ok(!itx.classList.contains('hidden') && pill.getAttribute('aria-expanded')==='true','the IT pill reveals the Italian explanation');
  }
  ok(JSON.stringify(rec3())===rec0,'reading records nothing');
  box.querySelector('.km-mode-btn[data-mode=practice]').click();
  ok(rows().length===n0 && !!box.querySelector('.km-vf'),'Answer them brings back the practice rows');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
