// Correct mock answers count in Today (maintainer, 2026-10-02): each day's correct answers on saved mocks become `x` in a shared slot of the daily log, derived from the mock history, so mocks taken before the change count too (backfill), two synced devices never count one mock twice, and Clear all results takes nothing back; shown in the ring and the dots, kept OUT of the pace behind the ready date; an abandoned mock adds nothing. Run: node scripts/check_daily_mock.js (UILANG=it-IT).
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
// Two past mocks two days ago (28 and 27 right), saved before Today counted mocks, and one yesterday (30).
const ago=n=>{const d=new Date(); d.setDate(d.getDate()-n); d.setHours(11,0,0,0); return d;};
const past=[[1,30],[2,28],[2,27]].map(([n,c],i)=>({date:new Date(ago(n).getTime()+i*60e3).toISOString(),correct:c,total:30,wrong:30-c,pass:c>=27,level:3,items:[]}));
w.localStorage.setItem('patente_exam_history',JSON.stringify(past));
setTimeout(()=>{
  w.confirm=()=>true;
  const key=n=>w.dayKey(ago(n)); const day=n=>w.loadDaily()[key(n)];
  ok(day(2) && day(2).x===55 && day(1).x===30,'backfill at launch: 55 two days ago, 30 yesterday');
  ok(w.dailyProgress(day(2))===55 && w.dailyProgress(day(2),false)===0,'the past days count them; the pace does not');
  w.syncMockDaily(); ok(day(2).x===55,'running it again changes nothing');
  // Another device with the same history: its bundle must not double the count.
  const other=JSON.parse(JSON.stringify(w.loadDaily())); other[key(2)].dv.dOTHER={a:5,c:5,m1:5};
  w.mergeDaily(other); ok(day(2).x===55,'merging another device\'s log with the same mocks: still 55');
  // A device still on 20261008d wrote x into its own share: it is folded into the slot.
  const d2=w.loadDaily(); d2[key(1)].dv[w.deviceId()]={x:30}; w.dailyTotals(d2[key(1)]); w.saveDaily(d2);
  w.syncMockDaily(); ok(day(1).x===30,'an x left in a device\'s own share by the previous build is not added twice');
  // Clear all results keeps the days already counted.
  w.localStorage.setItem('patente_exam_history','[]'); w.syncMockDaily(); ok(day(2).x===55,'Clear all results takes nothing back');
  const sheet=(nRight,finish=true)=>{ w.startExam();
    const es=w.eval('examState'); es.items.forEach((it,i)=>{ es.index=i; w.handleExamAnswer(i<nRight?it.stmt.answer:(it.stmt.answer==='VERO'?'FALSO':'VERO')); });
    if(finish) w.finishExam(); else w.abandonExam(); };
  const before=w.todayProgress(), rateBefore=JSON.stringify(w.studyRate());
  sheet(27);
  ok(w.todayProgress()===before+27,'a finished mock with 27 right adds 27 to Today ('+before+' -> '+w.todayProgress()+')');
  const d=w.loadDaily()[w.dayKey()];
  ok(d.x===27 && (d.a||0)===0 && (d.c||0)===0,'stored as x; the study answer counters are untouched');
  ok(d.dv._mocks && d.dv._mocks.x===27 && Object.entries(d.dv).every(([k,v])=>k==='_mocks'||!v.x),'kept in the shared mock slot, not a device\'s own share');
  ok(JSON.stringify(w.studyRate())===rateBefore,'the pace behind the ready date does not change');
  w.renderDailyLoop();
  ok(w.document.getElementById('daily-ring-num').textContent===String(before+27),'the dashboard ring shows it');
  const dot=[...w.document.querySelectorAll('#daily-strip *')].reverse().find(e=>/27/.test(e.title||e.getAttribute('aria-label')||''));
  ok(!!dot,'today\'s dot names the 27');
  sheet(20,false);
  ok(w.todayProgress()===before+27,'an abandoned mock adds nothing');
  sheet(30);
  ok(w.todayProgress()===before+57,'a second finished mock adds its 30');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
