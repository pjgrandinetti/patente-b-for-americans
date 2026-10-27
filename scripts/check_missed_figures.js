// Consistently missed figures (20261023q, maintainer, 2026-10-23): a "Consistently missed" chip on the Numbers tab shows the
// figures whose asked questions the learner missed in Italian and has not yet fixed, each with its count; the exam-date
// box's disclosure links to it. Run: node scripts/check_missed_figures.js (UILANG=it-IT; SRC= another public_html).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US', IT=LANG.startsWith('it');
const bank=JSON.parse(fs.readFileSync(root+'/questions.json','utf8')).filter(q=>(q.statements||[]).some(s=>!s.retired));
const ref=JSON.parse(fs.readFileSync(root+'/reference.json','utf8'));
const row=ref.numbers.find(n=>n.value==='130 km/h' && Array.isArray(n.asked) && n.asked.length>=3);
const cardOf={}; bank.forEach(q=>q.statements.forEach(s=>{cardOf[s.number]=q.id;}));
const key=n=>{const d=new Date(); d.setDate(d.getDate()+n); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
// Two of the row's questions missed at Italiano and still open (streak 0), one missed and fixed (streak 2).
const L={1:{},2:{},3:{}}; const [a,b,c]=row.asked;
const seed=(num,streak)=>{const id=cardOf[num]; const q=bank.find(x=>x.id===id); const full={}; q.statements.forEach(s=>{full[s.number]={seen:1,correct:1,streak:1,given:s.answer};});
  for(const l of [1,2,3]) if(!L[l][id]) L[l][id]={lastSeen:'2026-09-01T00:00:00.000Z',st:JSON.parse(JSON.stringify(full))};
  const st=q.statements.find(s=>s.number===num); L[3][id].st[num]={seen:3,correct:1,streak,miss:2,given:st.answer,dr:streak};};
// open: no correct day yet; fixed: correct on three different days (the review's own test, 20261023s)
seed(a,0); seed(b,0); seed(c,3);
// the expected rows: every row whose asked list holds one of the two open questions (a figure can sit in two rows, by road and by vehicle, and one question can turn on two figures)
// only a row holding BOTH open questions is listed (two or more missed, 20261023r)
// twin rows with the same value and asked list (the speeds by road and by vehicle) are shown once (20261023t)
const cand=ref.numbers.filter(n=>Array.isArray(n.asked)&&n.asked.includes(a)&&n.asked.includes(b));
// a row whose questions all sit inside another candidate's with the same value is the same figure split finer, shown once (20261026d)
const expRows=cand.filter((n,i)=>!cand.some((m,j)=>j!==i&&m.value===n.value&&n.asked.every(x=>m.asked.includes(x))&&(m.asked.length>n.asked.length||j<i)));
const expN=expRows.length;
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.localStorage.setItem('patente_level','3'); for (const l of [1,2,3]) w.localStorage.setItem('patente_progress_L'+l, JSON.stringify(L[l]));
w.localStorage.setItem('patente_exam_date',key(5));
const good=[1,0,1,1,0,2,1,0,1,1,0,1,1,0,1];
w.localStorage.setItem('patente_exam_history',JSON.stringify(good.map((x,i)=>{const d=new Date(); d.setDate(d.getDate()-1-i); return {date:d.toISOString(),correct:30-x,total:30,wrong:x,pass:true,level:3,items:[]};})));
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollTo=function(){}; w.Element.prototype.scrollIntoView=function(){}; w.alert=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const $=id=>w.document.getElementById(id);
setTimeout(()=>{
  w.italianoComplete=()=>true; w.renderDashboard();
  const box=$('exam-date-box'); const link=box&&box.querySelector('[data-ed=figures]');
  ok(link && new RegExp('(Figures consistently missed|Cifre sbagliate ripetutamente): '+expN+'$').test(link.textContent),'the exam-date disclosure links to the missed figures: '+(link&&link.textContent));
  link.click();
  ok(!$('screen-vocab').classList.contains('hidden'),'the link opens the Reference page');
  const chip=w.document.querySelector('.review-chip[data-cat=missed]');
  ok(chip && chip.classList.contains('active') && /(Consistently missed|Sbagliate ripetutamente)/.test(chip.textContent) && chip.querySelector('.review-chip-n').textContent===String(expN),'on the Consistently missed chip, counting '+expN+' rows: '+(chip&&chip.textContent));
  const rows=[...w.document.querySelectorAll('#review-numbers-body .review-row')];
  ok(rows.length===expN && expN>=1 && rows.every(r=>/130 km\/h/.test(r.textContent)),'only the rows holding both questions show, the 110 row with one miss does not: '+rows.length);
  const counts=rows.map(r=>(r.querySelector('.review-missed')?.textContent||'').match(/\d+/)?.[0]).sort().join(',');
  const expCounts=expRows.map(n=>String([a,b].filter(x=>n.asked.includes(x)).length)).sort().join(',');
  ok(counts===expCounts,'each row counts its open misses and not the fixed one: '+counts+' against '+expCounts);
  ok(rows.every(r=>r.classList.contains('is-short') && !r.querySelector('.review-ctx, .review-alt, .review-asked, .review-fine') && r.querySelector('.review-label') && r.querySelector('.review-value')),'each row is one short line and its figure, with no category, group, second language or Asked count');
  const shorts=rows.map(r=>r.querySelector('.review-label').textContent);
  ok(shorts.every(s=>expRows.some(n=>s===(IT?n.shortIt:n.shortEn)) && !/\(/.test(s) && s.length<=90),'each line is the row\'s own short phrase: '+shorts.join(' | '));
  ok(w.document.querySelectorAll('#review-numbers-body .review-cat-title').length===1 && !w.document.querySelector('#review-numbers-body .review-group-title, #review-numbers-body .review-group-head'),'one flat list, no category or group headings');
  ok(!w.document.querySelector('#review-numbers-body .review-group-note') && !w.document.querySelector('#review-numbers-body .review-foot'),'no group notes or footers on the chip, so the list stays short');
  w.document.querySelector('.review-chip[data-cat=all]').click();
  ok(w.document.querySelectorAll('#review-numbers-body .review-row').length>100 && !w.document.querySelector('#review-numbers-body .review-missed'),'All restores every row with no missed line');
  // a learner with no open miss gets no chip and no link
  for (const l of [1,2,3]) w.localStorage.setItem('patente_progress_L'+l, '{}'); w.eval('progress = {}');
  w.renderReviewNumbers(); w.renderDashboard();
  ok(!w.document.querySelector('.review-chip[data-cat=missed]') || w.document.querySelector('.review-chip[data-cat=missed]').querySelector('.review-chip-n').textContent==='0','with nothing missed the chip is absent or at zero');
  ok(!$('exam-date-box').querySelector('[data-ed=figures]'),'and the exam-date box has no link');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
