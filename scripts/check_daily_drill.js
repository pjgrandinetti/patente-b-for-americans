// A correct answer in the weak-spot drill counts in Today's number on the
// dashboard (maintainer, 2026-09-30: drilling showed "Today 0").
// Run: node scripts/check_daily_drill.js (UILANG=it-IT for the Italian face).
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
  const qs=w.eval('questions'); const picks=qs.slice(0,2).map(q=>({id:q.id,topic:q.topic,stmts:[String(q.statements[0].number),String(q.statements[1].number)],need:2}));
  // Every statement already cleared at the exam level, as when only the drill is left.
  for (const L of [1,2,3]) { w.setLevel(L);
    picks.forEach(p=>p.stmts.forEach(n=>{const r=w.stmtRecord(p.id,n); r.seen=3; r.correct=3; r.streak=3;})); w.saveProgress(); }
  w.difficultCards=()=>picks; w.drillEffort=()=>({questions:4,answers:8,days:1});
  const before=w.todayProgress();
  w.startDrill();
  const st=w.eval('questions').find(q=>q.id===picks[0].id).statements;
  const btn=(n,right)=>{const li=[...w.document.querySelectorAll('#card-statements li')].find(l=>l.innerHTML.includes(n)); const ans=st.find(s=>String(s.number)===n).answer; return li&&li.querySelector(((ans==='VERO')===right)?'.btn-vero':'.btn-falso');};
  const b1=btn(picks[0].stmts[0],true), b2=btn(picks[0].stmts[1],false);
  ok(b1&&b2,'the drill card shows its two statements');
  b1.click(); b2.click();
  ok(w.todayProgress()===before+1,'one correct drill answer adds one to Today, a wrong one adds none');
  w.renderDailyLoop();
  ok(w.document.getElementById('daily-ring-num').textContent===String(before+1),'the dashboard ring shows it');
  const d=w.loadDaily()[w.dayKey()];
  ok(d.w===1&&d.a>=2,'stored as w, with both answers counted in a');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
