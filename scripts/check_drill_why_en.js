// In the weak spots, "Why?" after a right answer at Solo italiano opens the statement's English (reported 2026-10-01): a language miss carries that English behind the drill's own pill, and Why? used to show the explanation and leave it hidden. A second tap folds it again; an Italian browser sees no English. Run: node scripts/check_drill_why_en.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US'; const IT=LANG.startsWith('it');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=function(){}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const qs=JSON.parse(fs.readFileSync(root+'/questions.json','utf8'));
const card=qs.find(q=>q.statements.some(s=>s.number==='22930')); const st=card.statements.find(s=>s.number==='22930');
const P={1:{[card.id]:{st:{'22930':{seen:1,correct:1,streak:1}}}},2:{},3:{[card.id]:{st:{'22930':{seen:2,correct:1,streak:0,miss:1}}}}};
for(const L of [1,2,3]) w.localStorage.setItem('patente_progress_L'+L,JSON.stringify(P[L]));
w.localStorage.setItem('patente_level','3');
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  w.document.querySelector('[data-screen="exam"]')?.click();
  w.eval('startDrill()');
  const li=()=>[...w.document.querySelectorAll('#card-statements li')].find(l=>l.querySelector('.stmt-number')?.textContent==='#22930');
  const en=()=>li().querySelector('.stmt-drill-en');
  if (IT) {
    ok(li() && !en(),'an Italian browser: no drill English at all');
    li().querySelector(st.answer==='VERO'?'.btn-vero':'.btn-falso').click();
    const why=li().querySelector('.stmt-why-btn'); why&&why.click();
    ok(!li().querySelector('.stmt-english-primary:not(.hidden)') && !li().querySelector('.stmt-drill-en'),'and none after Why?');
  } else {
    ok(li() && en() && en().classList.contains('hidden'),'a language miss carries its English behind the drill pill, hidden');
    li().querySelector(st.answer==='VERO'?'.btn-vero':'.btn-falso').click();
    ok(en().classList.contains('hidden'),'a right answer shows no English on its own');
    const why=li().querySelector('.stmt-why-btn');
    ok(!!why,'the Why? button is there');
    why.click();
    ok(!en().classList.contains('hidden') && en().textContent===st.english_translation,'Why? opens the statement\'s English');
    ok(!li().querySelector('.stmt-expl-box').classList.contains('hidden') && li().querySelector('.stmt-english-expl'),'with the explanation and its English');
    ok(li().querySelectorAll('.stmt-why-en').length===0,'no second copy of the English');
    why.click();
    ok(en().classList.contains('hidden') && li().querySelector('.stmt-expl-box').classList.contains('hidden'),'a second tap folds them again');
  }
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
