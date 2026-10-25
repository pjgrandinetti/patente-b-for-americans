// In the weak-spot drill, Next skips cards already answered this round
// (maintainer, 2026-09-30).
// Run: node scripts/check_drill_next.js (UILANG=it-IT for the Italian face).
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
  const qs=w.eval('questions'); const picks=qs.slice(0,4).map(q=>({id:q.id,topic:q.topic,stmts:[String(q.statements[0].number)],need:2}));
  w.difficultCards=()=>picks; w.drillEffort=()=>({questions:4,answers:8,days:1});
  w.confirm=()=>true;
  w.startDrill();
  const idx=()=>w.eval('session.index'), next=()=>w.document.getElementById('btn-next');
  const answer=()=>[...w.document.querySelectorAll('#card-statements .btn-vero')].forEach(b=>b.click());
  w.eval('session.index=2'); w.renderStudyCard(); answer();          // card 3 answered first, out of order
  w.eval('session.index=0'); w.renderStudyCard(); answer();
  next().click(); ok(idx()===1,'Next from card 1 goes to card 2');
  answer(); next().click(); ok(idx()===3,'Next from card 2 skips the answered card 3 and lands on card 4');
  answer();
  ok(/finish|fine|termina|concludi/i.test(next().textContent),'with nothing left, the button offers to finish ('+next().textContent+')');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
