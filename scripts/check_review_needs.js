// The exam-date box's closed disclosure "What is waiting in the review" (20261023c, maintainer, 2026-10-23): the
// pool counted by how many correct days each question still needs, and the minimum answers before it is empty.
// Run: node scripts/check_review_needs.js (UILANG=it-IT; SRC= another public_html).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US';
const bank=JSON.parse(fs.readFileSync(root+'/questions.json','utf8')).filter(q=>(q.statements||[]).some(s=>!s.retired));
const live=q=>q.statements.filter(s=>!s.retired);
const key=n=>{const d=new Date(); d.setDate(d.getDate()+n); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
// 30 questions due: 10 with two correct days (dr 2), 12 with one (dr 1), 8 with none (streak 0, no dr).
const L={1:{},2:{},3:{}}; const cards=bank.slice(0,30);
cards.forEach((q,i)=>{ const st=live(q)[0]; const full={}; q.statements.forEach(s=>{full[s.number]={seen:1,correct:1,streak:1,given:s.answer};});
  for(const l of [1,2,3]) L[l][q.id]={lastSeen:'2026-09-01T00:00:00.000Z',st:JSON.parse(JSON.stringify(full))};
  const r={seen:5,correct:2,streak:0,miss:3,given:st.answer};
  if(i<10){r.dr=2;r.dd=key(-1);r.streak=2;} else if(i<22){r.dr=1;r.dd=key(-2);r.streak=1;}
  L[3][q.id].st[st.number]=r; });
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
  w.italianoComplete=()=>true; w.renderDashboard();
  const box=$('exam-date-box'); const det=box&&box.querySelector('details.exam-date-pool');
  ok(w.dailyReviewPool().length===30,'30 questions are in the pool');
  ok(det && !det.open,'the box carries a closed disclosure');
  ok(det && /(What is waiting in the review|Cosa resta nel ripasso)/.test(det.querySelector('summary').textContent),'with its summary line');
  const cells=det?[...det.querySelectorAll('tbody td.num')].map(td=>td.textContent):[];
  ok(cells.join(',')==='10,12,8','the rows count one, two and three correct days still needed: '+cells.join(','));
  ok(/(At least 58 more correct answers|Almeno 58 altre risposte corrette)/.test(det.textContent),'and the minimum answers left is 58: '+det.textContent.replace(/\s+/g,' ').slice(-200));
  det.open=true; det.dispatchEvent(new w.Event('toggle')); w.renderDashboard();
  ok(box.querySelector('details.exam-date-pool').open,'the open state survives a redraw');
  // answer one of the dr-2 questions today through the review: it leaves the pool and the table
  w.reviewPerDay=()=>10; w.startDailyReview();
  const item=w.document.querySelector('#card-statements .statement-item'); item.querySelector(item.dataset.answer==='VERO'?'.btn-vero':'.btn-falso').click();
  w.showScreen('dashboard'); w.renderDashboard();
  const c2=[...$('exam-date-box').querySelectorAll('tbody td.num')].map(td=>td.textContent);
  ok(c2.reduce((a,b)=>a+Number(b),0)===29,'an answer today takes its question out of the table: '+c2.join(','));
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
