// Each Reference figure says how many questions turn on it (20261010z, maintainer, 2026-10-04): a muted "Asked in N questions" under the label, shown with the values hidden too, absent on rows whose number is never tested and on the row that already names its wrong value. Run: node scripts/check_ref_asked.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US', IT=LANG.startsWith('it');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  const ref=JSON.parse(fs.readFileSync(root+'/reference.json','utf8'));
  w.document.querySelector('[data-screen="vocab"]')?.click();
  w.document.querySelector('.review-section-btn[data-section="numbers"]')?.click();
  const box=w.document.getElementById('review-pane-numbers')||w.document;
  const lines=[...box.querySelectorAll('.review-asked')];
  const expect=ref.numbers.filter(n=>!n.untested && !n.wrong).reduce((a,n)=>a+(Array.isArray(n.group)?n.group.length:1),0);  // a row in two groups is drawn twice
  ok(lines.length===expect,'one count line per tested row without a wrong-value line: '+lines.length+' of '+expect);
  const r130=[...box.querySelectorAll('.review-row')].find(r=>/130 km\/h/.test(r.textContent) && r.querySelector('.review-asked'));
  const n130=ref.numbers.find(n=>n.value==='130 km/h').asked.length;
  ok(r130 && r130.querySelector('.review-asked').textContent===(IT?`Chiesta in ${n130} domande`:`Asked in ${n130} questions`),'the 130 km/h row: '+(r130&&r130.querySelector('.review-asked').textContent));
  const one=lines.find(l=>/ 1 /.test(l.textContent+' '));
  ok(one && one.textContent===(IT?'Chiesta in 1 domanda':'Asked in 1 question'),'singular for one');
  ok(![...box.querySelectorAll('.review-safe.review-untested')].some(m=>m.closest('.review-row').querySelector('.review-asked')),'no count on a row whose number is never tested');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
