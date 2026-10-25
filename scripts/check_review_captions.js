// Review image captions carry the same pill as the paragraphs (20261010j, maintainer, 2026-10-04): in the Italian notes an EN pill reveals the English caption, in the English notes an IT pill the Italian one, paired by image file; an Italian browser gets none. Run: node scripts/check_review_captions.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US', IT=LANG.startsWith('it');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true}); const w=dom.window;
Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollTo=function(){}; w.Element.prototype.scrollIntoView=function(){}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  const tr=JSON.parse(fs.readFileSync(root+'/topic_reviews.json','utf8'));
  const topic=Object.keys(tr).find(k=>k.startsWith('Definizioni stradali'));
  const body=()=>w.document.getElementById('review-body');
  const show=lang=>{ w.eval(`reviewTopic=${JSON.stringify(topic)}; reviewLang=${JSON.stringify(lang)};`); w.renderReviewBody(); return [...body().querySelectorAll('figcaption')]; };
  if (IT) {
    const caps=show('it');
    ok(caps.length>0 && caps.every(c=>!c.querySelector('.rb-it')),'an Italian browser: captions, and no pill on any');
  } else {
    let caps=show('it');
    ok(caps.length>=2 && caps.every(c=>c.querySelector('.rb-it')?.textContent==='EN'),'Italian notes: every caption has an EN pill ('+caps.length+')');
    const panel=caps.find(c=>/rimorchi/.test(c.textContent));
    const txt=panel.querySelector('.rb-itxt');
    ok(txt.classList.contains('hidden') && /trailer/i.test(txt.textContent),'the English caption is hidden until asked: '+txt.textContent);
    panel.querySelector('.rb-it').click(); ok(!txt.classList.contains('hidden'),'the pill reveals it');
    w.setItAll(false); ok(txt.classList.contains('hidden'),'and the header control folds it with the rest');
    caps=show('en'); ok(caps.every(c=>c.querySelector('.rb-it')?.textContent==='IT'),'English notes: every caption has an IT pill');
    // every topic, both directions
    let none=0,total=0;
    for (const k of Object.keys(tr)) { if(!tr[k].en) continue; w.eval(`reviewTopic=${JSON.stringify(k)}; reviewLang='it';`); w.renderReviewBody(); for (const c of body().querySelectorAll('figcaption')) { total++; if(!c.querySelector('.rb-it')) none++; } }
    ok(total>300 && none===0,'all '+total+' captions in the Italian notes carry a pill');
  }
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
