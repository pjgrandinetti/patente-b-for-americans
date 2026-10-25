// The drill share of the ready date charges each weak-spot answer at DRILL_TIME_FACTOR (2) ordinary answers (maintainer, 2026-09-30).

// Run: node scripts/check_drill_time.js (UILANG=it-IT for the Italian face).
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
  w.difficultCards=()=>[{id:1,stmts:['a','b','c','d','e'],need:2},{id:2,stmts:['f','g','h','i','j'],need:2}];
  w.studyRate=()=>({rate:2,perStudyDay:2,days:1,studied:1});
  w.eval('invalidateDrillMemo()');
  const e=w.drillEffort();
  ok(e.answers===4,'the answers owed are the real count ('+e.answers+')');
  ok(e.days===4,'the days double: 4 answers at 2 a day, charged twice, is 4 days ('+e.days+')');
  // The span in words (20261009d): minutes or hours while the work fits in a day, whole days beyond.
  const it=(process.env.UILANG||'').startsWith('it');
  const words=(answers,days)=>w.drillSpanWords({answers,minutes:answers,days});
  ok(words(6,1)===(it?'6 minuti':'6 minutes'),'six answers within a day: '+words(6,1)+', not one day');
  ok(words(23,1)===(it?'25 minuti':'25 minutes') && words(70,1)===(it?'un’ora':'one hour') && words(200,1)===(it?'3 ore':'3 hours'),'longer work in round minutes and hours: '+[words(23,1),words(70,1),words(200,1)].join(', '));
  ok(words(300,3)===(it?'3 giorni':'3 days'),'more than a day of study: whole days, as before');
  // The minutes come from the learner's own time per question, doubled (20261009e); 30 s stands in when nothing is measured.
  ok(w.drillSecondsPerAnswer()===60,'nothing measured: 30 seconds doubled, a minute an answer');
  w.avgSecondsPerQuestion=()=>19; ok(w.drillSecondsPerAnswer()===38,'19 seconds a question measured: 38 seconds a weak-spot answer');
  w.difficultCards=()=>[{id:1,topic:w.eval('questions')[0].topic,stmts:['a','b','c'],need:6,weight:3}]; w.eval('invalidateDrillMemo()');
  ok(w.drillEffort().minutes===4,'six answers at 38 seconds: 4 minutes ('+w.drillEffort().minutes+')');
  w.avgSecondsPerQuestion=()=>null; w.eval('invalidateDrillMemo()');
  w.difficultCards=()=>[{id:1,topic:w.eval('questions')[0].topic,stmts:['a','b','c'],need:6,weight:3}]; w.studyRate=()=>({rate:150,perStudyDay:150,days:5,studied:5}); w.eval('invalidateDrillMemo()');
  w.italianoComplete=()=>true; w.renderDashboard();
  const sub=w.document.getElementById('weak-sub')?.textContent || w.document.getElementById('weak-spots').textContent;
  ok(/(about 6 minutes|circa 6 minuti)/.test(sub) && !/(one day|un giorno)/.test(sub),'the dashboard card says about 6 minutes: '+sub.replace(/\s+/g,' ').slice(-80));
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
