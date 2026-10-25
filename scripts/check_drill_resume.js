// Leaving the weak-spot drill by the Home icon keeps its place: starting it again
// opens at the first card still unanswered, not at the top (maintainer, 2026-09-29).
// Run: node scripts/check_drill_resume.js (UILANG=it-IT for the Italian face).
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
  const qs=w.eval('questions'); const picks=qs.slice(0,3).map(q=>({id:q.id,topic:q.topic,stmts:[String(q.statements[0].number),String(q.statements[1].number)],need:2}));
  w.difficultCards=()=>picks; w.drillEffort=()=>({questions:6,answers:12,days:1});
  let topic=null; w.resumableTopic=()=>topic;
  w.startDrill();
  ok(w.eval('session.index')===0,'the drill opens at the first card');
  [...w.document.querySelectorAll('#card-statements .btn-vero')].forEach(b=>b.click());
  w.document.getElementById('nav-logo').click();
  ok(w.document.getElementById('screen-dashboard').classList.contains('active'),'Home shows the dashboard');
  ok(w.drillOpen(),'the drill round is still open after Home');
  ok(!w.document.getElementById('nav-resume').classList.contains('hidden'),'the Resume button is shown');
  w.resumeStudy();
  ok(w.eval('session.buildMode')==='drill','Resume goes back into the drill');
  ok(w.eval('session.index')===0,'and opens on the card the learner left (20261005x), not a rebuilt round');
  ok(w.cardUnansweredCount(picks[0].id)===0,'the first card keeps its answers');
  w.document.getElementById('nav-logo').click();
  topic='Segnali di pericolo'; let topicStarted=0; const orig=w.startStudySession; w.startStudySession=()=>{topicStarted++};
  w.resumeStudy();
  ok(topicStarted===1,'after Home, a topic with work takes Resume');
  w.startStudySession=orig;
  w.startDrill();
  ok(w.eval('session.index')===1,'the drill started from Final Stretch still resumes at the second card');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
