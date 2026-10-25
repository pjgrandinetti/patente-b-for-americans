// With mocks on record and the 5% bar not met, the done block gives no date and no count of further mocks (20261009w, maintainer, 2026-10-03: the count swung 32, 8, never, 27, 23, 7, 15, 1 on his own mocks); it names the bar. With no mock on record the flat three days stand. Run: node scripts/check_mock_plan.js (UILANG=it-IT).
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
// wrongs newest first; `perDay` mocks on each earlier day, counting back from yesterday.
const hist=(wr,perDay=2)=>wr.map((x,i)=>{const d=new Date(); d.setDate(d.getDate()-1-Math.floor(i/perDay)); d.setHours(18,0,0,0); return {date:new Date(d.getTime()-(i%perDay)*600e3).toISOString(),correct:30-x,total:30,wrong:x,pass:x<=3,level:3,items:[]};});
setTimeout(()=>{
  const proj=()=>w.document.getElementById('daily-projection');
  const set=wr=>w.localStorage.setItem('patente_exam_history',JSON.stringify(wr));
  const fmt=n=>{const d=new Date(); d.setDate(d.getDate()+n); return new Intl.DateTimeFormat(it?'it-IT':'en-US',{month:'short',day:'numeric'}).format(d);};
  w.remainingAcrossLevels=()=>0; w.italianoComplete=()=>true; w.difficultCards=()=>[]; w.drillEffort=()=>null;
  const draw=()=>{ w.renderDailyLoop(); return proj().textContent; };
  set([]); let txt=draw();
  ok(txt.includes(fmt(3)) && !/(Keep taking|Continua a far)/.test(txt),'no mock on record: the flat three days, as before');
  const his=[1,2,1,2,1,2,2,1,2]; set(hist(his,7)); txt=draw();
  ok(/(Keep taking them until your chance of failing is 5% or less|Continua a farle finché la probabilità di non superare l’esame è del 5% o meno)/.test(txt),'nine mocks, bar not met: the block names the bar: '+txt.replace(/\s+/g,' ').slice(-130));
  ok(!proj().querySelector('a.exam-plan-step') && !/(at your current pace|al ritmo attuale|more mock|altre \d+)/i.test(txt) && !/\d+ (days|giorni)/.test(txt.replace(/14/g,'')),'and gives no date and no count of mocks');
  ok(typeof w.mockPlan==='undefined' && typeof w.mockReadyAt==='undefined','the count is gone from the code');
  const good=[1,0,1,1,0,2,1,0,1,1,0,1,1,0,1]; set(hist(good,3)); txt=draw();
  ok(/now|già ora/.test(txt) && !!proj().querySelector('a.exam-plan-step'),'fifteen mocks at the bar: ready now');
  set(hist(Array(15).fill(2),3)); txt=draw();
  ok(/(Keep taking|Continua a far)/.test(txt) && !proj().querySelector('a.exam-plan-step'),'fifteen at 2 wrong: the same line, no date');
  // Weak spots beside open mocks: their time is named, still no date.
  set(hist(his,7)); const rp0=w.reserveParts;
  w.drillEffort=()=>({questions:3,answers:6,minutes:4,days:1}); w.reserveParts=()=>({drill:1,mocks:3});
  txt=draw();
  ok(/(about 4 minutes|circa 4 minuti)/.test(txt) && /(Keep taking mock exams|Continua a fare simulazioni)/.test(txt) && !proj().querySelector('a.exam-plan-step'),'four minutes of weak spots and open mocks: both named, no date');
  // At the bar with weak spots left: only the weak spots are dated.
  set(hist(good,3)); w.difficultCards=()=>[{stmts:[1,2,3]}]; txt=draw();
  ok(txt.includes(fmt(1)) && !/(Keep taking|Continua a far)/.test(txt),'mocks at the bar, weak spots left: the date is the weak spots alone');
  w.difficultCards=()=>[]; w.reserveParts=rp0;
  // Before the levels are cleared the reserve is the flat allowance.
  w.drillEffort=()=>({questions:10,answers:20,days:1}); set(hist(his,7));
  ok(w.reserveParts(w.loadDaily()).mocks===3,'the reserve before the levels are cleared is the flat three days');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
