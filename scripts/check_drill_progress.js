// In the weak-spot drill the progress line counts the drill's own cards, and the
// label says how many questions are still to clear (maintainer, 2026-09-29).
// Run: node scripts/check_drill_progress.js (UILANG=it-IT for the Italian face).
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
  w.difficultCards=()=>picks; w.drillEffort=()=>({questions:5,answers:10,days:1});
  w.startDrill();
  const bar=w.document.getElementById('study-progress-bar'), lab=()=>w.document.getElementById('study-progress-label').textContent;
  const grow=cls=>[...bar.children].filter(s=>cls?s.classList.contains('is-done'):!s.classList.contains('is-done')).reduce((n,s)=>n+Number(s.style.flexGrow||1),0);
  ok(w.eval('session.buildMode')==='drill','the drill session started');
  ok(grow(true)===0 && grow(false)===3,'the bar spans the three drill cards, none done');
  ok(/0 (of|di) 3/.test(lab()) && /\b5\b/.test(lab()),'label: 0 of 3 cards, 5 questions still to clear ('+lab()+')');
  const btns=[...w.document.querySelectorAll('#card-statements .btn-vero')];
  ok(btns.length===2,'the card shows only its two drill questions');
  btns.forEach(b=>b.click());
  ok(grow(true)===1 && grow(false)===2,'after answering the card: one of three done');
  ok(/1 (of|di) 3/.test(lab()),'label follows ('+lab()+')');
  ok(!/849/.test(lab()),'the whole bank is not counted');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
