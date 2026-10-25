// Resume after a trip to the Reference page puts the learner back on the drill
// card they were working on, not on the first card still unanswered
// (maintainer, 2026-09-30). Run: node scripts/check_drill_return.js (UILANG=it-IT for Italian).
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
  const qs=w.eval('questions'); let picks=qs.slice(0,4).map(q=>({id:q.id,topic:q.topic,stmts:[String(q.statements[0].number),String(q.statements[1].number)],need:2}));
  w.difficultCards=()=>picks; w.drillEffort=()=>({questions:8,answers:16,days:1});
  w.resumableTopic=()=>'Segnali di pericolo';
  w.startDrill();
  const ans=()=>[...w.document.querySelectorAll('#card-statements .btn-vero')];
  ans().forEach(b=>b.click());
  w.eval('session.index=2'); w.renderStudyCard();
  const target=w.eval('session.queue[2]');
  ans()[0].click();
  w.document.getElementById('nav-vocab').click();
  ok(w.document.getElementById('screen-vocab').classList.contains('active'),'Reference is shown');
  picks=[picks[3],picks[1],picks[0],picks[2]];   // the ranking shifts meanwhile
  w.resumeStudy();
  ok(w.document.getElementById('screen-study').classList.contains('active'),'Resume shows the study screen');
  ok(w.eval('session.buildMode')==='drill','still in the drill');
  ok(w.eval('session.queue[session.index]')===target,'on the card the learner left, not the first unanswered one');
  ok(w.cardUnansweredCount(target)===1,'with its answer kept');
  ok(w.eval('currentLevel')===3&&!!w.eval('_drillStmts'),'at the drill level, with the drill filter back');
  w.document.getElementById('nav-logo').click();
  w.resumeStudy();
  ok(w.eval('session.buildMode')!=='drill','after Home, a topic with work still takes Resume');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
