// Mock exam timings (maintainer, 2026-10-01): the time each statement is on screen, summed over visits and stopped on the Riepilogo and while the app is away; the time used on the result; a Time column in Past Results (a dash for mocks saved before); per-question seconds in the review with the three slowest marked. The clock is controlled. Run: node scripts/check_exam_timing.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US'; const IT=LANG.startsWith('it');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.localStorage.setItem('patente_level','3');
w.localStorage.setItem('patente_exam_history', JSON.stringify([{date:'2026-09-01T10:00:00.000Z',correct:29,total:30,wrong:1,pass:true,level:3,items:[]}]));
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=function(){}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
let vis='visible'; Object.defineProperty(w.document,'visibilityState',{get:()=>vis,configurable:true});
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const $=id=>w.document.getElementById(id);
setTimeout(()=>{
  let T=1_800_000_000_000; const realNow=w.Date.now; w.Date.now=()=>T; const adv=sec=>{T+=sec*1000;};
  w.document.querySelector('.nav-btn[data-screen="exam"]').click();
  w.startExam();                       // statement 1 on screen
  adv(5);  w.goExamStatement(1);       // s1 = 5
  adv(12); w.goExamStatement(0);       // s2 = 12
  adv(3);  w.showExamSummary();        // s1 = 8; the Riepilogo is not counted
  adv(60); w.goExamStatement(2);
  adv(20); vis='hidden'; w.document.dispatchEvent(new w.Event('visibilitychange'));   // s3 = 20, then away
  adv(100); vis='visible'; w.document.dispatchEvent(new w.Event('visibilitychange'));
  adv(4);
  const dw=w.eval('examState.dwell').slice(0,3).map(ms=>ms/1000);
  ok(dw[0]===8 && dw[1]===12 && dw[2]===20,'time per statement while open: '+dw.join(', ')+' (the away time and the Riepilogo not counted)');
  w.finishExam();
  ok(w.eval('examState.dwell')[2]/1000===24,'the open statement is closed out at finish');
  const used=$('exam-time-used')?.textContent||'';
  ok(/3:24/.test(used) && /20:00/.test(used) && (IT?/secondi a domanda/:/seconds per question/).test(used),'result: '+used);
  const h=JSON.parse(w.localStorage.getItem('patente_exam_history'));
  ok(h[0].time===204 && h[0].items[0].s===8 && h[0].items[1].s===12 && h[0].items[2].s===24 && h[0].items[3].s===0,'saved with the result: time 204 s and seconds per statement');
  w.updateExamAvailability();
  const rows=[...$('exam-history-table').querySelectorAll('tbody tr')];
  const th=[...$('exam-history-table').querySelectorAll('th')].map(x=>x.textContent);
  ok(th.includes(IT?'Tempo':'Time'),'Past Results has a Time column');
  ok(rows[0].children[3].textContent==='3:24' && rows[1].children[3].textContent==='–','the new mock shows 3:24, the old one a dash');
  $('btn-review-exam')?.click();
  const rev=[...$('exam-review').querySelectorAll('.exam-rev-item')];
  const tm=i=>rev[i].querySelector('.exam-rev-time')?.textContent||'';
  ok(/^8 s/.test(tm(0)) && /^12 s/.test(tm(1)) && /^24 s/.test(tm(2)),'review shows seconds: '+[tm(0),tm(1),tm(2)].join(' | '));
  ok([0,1,2].every(i=>rev[i].querySelector('.exam-rev-time.is-slow')) && rev.filter(r=>r.querySelector('.is-slow')).length===3,'the three slowest are marked, and only three');
  ok(/slowest|più lente/.test(tm(2)),'with a label');
  w.Date.now=realNow;
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
