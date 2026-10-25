// The ▶ button is not hidden by a stale weak-spot count, and it is refreshed on
// every screen change (maintainer, 2026-09-30).
// Run: node scripts/check_resume_fresh.js (UILANG=it-IT for the Italian face).
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
  const btn=w.document.getElementById('nav-resume');
  const qs=w.eval('questions'); const picks=qs.slice(0,2).map(q=>({id:q.id,topic:q.topic,stmts:[String(q.statements[0].number)],need:2}));
  w.resumableTopic=()=>null; w.drillOpen=()=>false;
  let list=[]; w.difficultCards=()=>list;
  w.drillEffort(); list=picks;             // memo holds an EMPTY list, then the list grows (a sync pull)
  w.renderDashboard();
  ok(!btn.classList.contains('hidden'),'dashboard shows the button although the memo was stale');
  list=[]; w.renderDashboard();
  ok(btn.classList.contains('hidden'),'nothing left: hidden');
  list=picks; w.showScreen('exam');
  ok(!btn.classList.contains('hidden'),'a screen change refreshes the button');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
