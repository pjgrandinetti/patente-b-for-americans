// In the weak-spot drill a floating pill counts the weak-spot questions still to clear (maintainer, 2026-09-30).

// Run: node scripts/check_drill_float.js (UILANG=it-IT for the Italian face).
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
  let owed=5; w.difficultCards=()=>picks; w.drillEffort=()=>({questions:owed,answers:10,days:1});
  const pill=()=>w.document.getElementById('float-drill');
  const shown=()=>!!pill() && !pill().classList.contains('hidden');
  w.startDrill();
  // jsdom lays nothing out, so the header always reads as scrolled away and
  // Today's pill floats; put the header back in view for the first checks.
  w.document.getElementById('float-daily').classList.add('hidden'); w.updateFloatDrill();
  ok(shown(),'the pill shows in the drill');
  ok(/\b5\b/.test(pill().querySelector('.uf-full').textContent),'it counts the questions still to clear ('+pill().querySelector('.uf-full').textContent+')');
  ok(/\b5\b/.test(pill().querySelector('.uf-mini').textContent),'a short form for a phone ('+pill().querySelector('.uf-mini').textContent+')');
  owed=4; [...w.document.querySelectorAll('#card-statements .btn-vero')][0].click();
  ok(/\b4\b/.test(pill().querySelector('.uf-full').textContent),'it follows an answer ('+pill().querySelector('.uf-full').textContent+')');
  const daily=w.document.getElementById('float-daily');
  daily.classList.remove('hidden'); w.updateFloatDrill();
  ok(!shown(),'with Today\'s pill floating, this pill stands down (they overlapped, 20261006d)');
  const inner=daily.querySelector('.daily-float-drill');
  ok(!!inner && /\b4\b/.test(inner.textContent),'and the count rides inside Today\'s pill ('+(inner&&inner.textContent)+')');
  w.updateStudyDailyPill();
  ok(!!daily.querySelector('.daily-float-drill'),'a redraw of Today\'s pill keeps the count');
  daily.classList.add('hidden'); w.updateFloatDrill();
  ok(shown() && !daily.querySelector('.daily-float-drill'),'header back in view: the pill returns, Today\'s pill loses the count');
  w.showScreen('dashboard');
  ok(!shown(),'it hides off the study screen');
  const t=qs.find(q=>q.topic)?.topic; w.startStudySession('topic',t);
  ok(!shown(),'it does not show in an ordinary topic session');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
