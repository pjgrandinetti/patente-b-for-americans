// The dashboard's weak-spots card sits above the level buttons, on a fresh page
// and on a stale cached one (maintainer, 2026-09-30).
// Run: node scripts/check_weak_card.js (UILANG=it-IT for the Italian face).
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
  const d=w.document, box=()=>d.getElementById('weak-spots'), sel=()=>d.getElementById('level-selector');
  const before=()=>!!(box().compareDocumentPosition(sel()) & w.Node.DOCUMENT_POSITION_FOLLOWING);
  ok(before(),'index.html puts the card above the level buttons');
  d.getElementById('topic-progress-grid').before(box());   // the old order, as a stale page has it
  ok(!before(),'stale order reproduced');
  w.renderWeakSpots();
  ok(before() && (box().nextElementSibling===sel() || box().parentElement.id==='dash-next' && box().parentElement.nextElementSibling===sel()),'renderWeakSpots moves it back above the buttons (inside the row with the mock card since 20261006l)');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
