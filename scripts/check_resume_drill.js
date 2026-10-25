// With every card cleared and weak spots left, the nav keeps a Begin/Resume button
// that starts the drill (maintainer, 2026-09-29).
// Run: node scripts/check_resume_drill.js (UILANG=it-IT for the Italian face).
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
  const btn=w.document.getElementById('nav-resume'), lab=()=>w.document.getElementById('nav-resume-label').textContent;
  let drilled=0, topicStarted=0; w.startDrill=()=>{drilled++}; w.startStudySession=()=>{topicStarted++};
  const set=(topic,effort,open)=>{ w.resumableTopic=()=>topic; w.drillEffort=()=>effort; w.drillOpen=()=>open; w.updateResumeButton(); };
  const E={questions:12,answers:20,days:2};
  set(null,E,false);
  ok(!btn.classList.contains('hidden'),'all cleared, weak spots left, no round open: button shown');
  ok(lab()===(it?'Inizia':'Begin'),'labelled Begin');
  ok(/weak-spot|punti deboli/.test(btn.title),'tooltip names the drill');
  w.resumeStudy(); ok(drilled===1&&topicStarted===0,'pressing it starts the drill');
  set(null,E,true);
  ok(!btn.classList.contains('hidden')&&lab()===(it?'Riprendi':'Resume'),'round open: Resume');
  w.resumeStudy(); ok(drilled===2,'pressing it resumes the drill');
  set(null,null,false);
  ok(btn.classList.contains('hidden'),'nothing left at all: hidden');
  w.resumeStudy(); ok(drilled===2&&topicStarted===0,'and pressing does nothing');
  set('Segnali di pericolo',E,false);
  ok(!btn.classList.contains('hidden')&&topicStarted===0,'a topic with work still takes the button');
  w.resumeStudy(); ok(topicStarted===1&&drilled===2,'and opens the topic, not the drill');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
