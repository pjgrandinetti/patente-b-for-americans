// With every level cleared, the dashboard still gives a ready date (maintainer, 2026-09-29).
// Run: node scripts/check_done_date.js (UILANG=it-IT for the Italian face).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US', it=LANG.startsWith('it');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  const proj=()=>w.document.getElementById('daily-projection');
  w.remainingAcrossLevels=()=>0;
  const run=(drill,ready)=>{ w.reserveParts=()=>drill==null?null:{drill,mocks:3}; w.examReady=()=>({ready,chance:ready?0.97:0.8,n:15}); w.renderDailyLoop(); return proj().textContent; };
  let txt=run(1,false);
  ok(/all three|tutti e tre|cleared|superate/.test(txt),'says every question is cleared');
  ok(!!proj().querySelector('a.exam-plan-step'),'the ready word is linked');
  const d=new Date(); d.setDate(d.getDate()+4);
  const f=new Intl.DateTimeFormat(it?'it-IT':'en-US',{month:'short',day:'numeric'}).format(d);
  ok(txt.includes(f),'weak spots 1 day + mocks 3 days: the date is four days out ('+f+')');
  txt=run(null,false);
  const d3=new Date(); d3.setDate(d3.getDate()+3);
  ok(txt.includes(new Intl.DateTimeFormat(it?'it-IT':'en-US',{month:'short',day:'numeric'}).format(d3)),'no weak spots: three days for the mocks');
  txt=run(2,true);
  const d2=new Date(); d2.setDate(d2.getDate()+2);
  ok(txt.includes(new Intl.DateTimeFormat(it?'it-IT':'en-US',{month:'short',day:'numeric'}).format(d2)) && !/mock exams, about|simulazioni, circa/.test(txt),'mocks already at the bar: only the weak spots count');
  txt=run(null,true);
  ok(/now|già ora/.test(txt) && !!proj().querySelector('a.exam-plan-step'),'nothing left: ready now, still linked');
  { const d=new Date(); d.setDate(d.getDate()+9); const k=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
    w.localStorage.setItem('patente_exam_date',k); txt=run(1,false);
    w.italianoComplete=()=>true; txt=run(1,false);
    ok(!proj().querySelector('a.exam-plan-step') && !/(you could be|potresti essere)/.test(txt) && !/(What remains|Restano)/.test(txt),'with an exam date entered (the review stage): no ready date and no "what remains" line (20261011k)');
    txt=run(null,true); ok(!/now|già ora/.test(txt) && !proj().querySelector('a.exam-plan-step'),'and no ready-now line');
    w.localStorage.removeItem('patente_exam_date'); }
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
