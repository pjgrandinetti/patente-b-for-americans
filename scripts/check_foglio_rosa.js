// The foglio rosa in the pass box (20261030v, maintainer, 2026-10-30): the two dates printed on it, the
// driving test possible from a month after the issue, the days left, and the three 2-hour lesson blocks.
// Run: node scripts/check_foglio_rosa.js (UILANG=it-IT; SRC= another public_html).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US', IT=LANG.startsWith('it');
const key=n=>{const d=new Date(); d.setDate(d.getDate()+n); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.localStorage.setItem('patente_level','3');
w.localStorage.setItem('patente_exam_outcome',JSON.stringify([{d:key(-1),r:'pass'}]));
w.localStorage.setItem('patente_pass_celebrated','1');
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollTo=function(){}; w.Element.prototype.scrollIntoView=function(){}; w.alert=()=>{};
w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const $=id=>w.document.getElementById(id);
setTimeout(()=>{
  w.italianoComplete=()=>true; w.renderDashboard();
  let box=$('exam-date-box');
  ok(!!box.querySelector('input[data-fr=iss]') && !!box.querySelector('input[data-fr=exp]') && !!box.querySelector('.exam-date-advice'),'before the dates: the two inputs and the general foglio rosa line');
  // An expiry before the issue is refused.
  box.querySelector('input[data-fr=iss]').value=key(0); box.querySelector('input[data-fr=exp]').value=key(-5);
  box.querySelector('[data-ed=frsave]').click();
  ok(!w.localStorage.getItem('patente_foglio_rosa'),'an expiry before the issue date is refused');
  box=$('exam-date-box');
  box.querySelector('input[data-fr=iss]').value=key(0); box.querySelector('input[data-fr=exp]').value=key(363);
  box.querySelector('[data-ed=frsave]').click();
  box=$('exam-date-box');
  const st=JSON.parse(w.localStorage.getItem('patente_foglio_rosa')||'null');
  ok(st && st.iss===key(0) && st.exp===key(363),'the two dates are stored');
  ok(/(Your foglio rosa|Il tuo foglio rosa)/.test(box.textContent) && !box.querySelector('input[data-fr]'),'the box shows the foglio rosa, not the form');
  ok(/(363 days left|mancano 363 giorni)/.test(box.querySelector('[data-row=valid] dd').textContent),'valid until, with the days left: '+box.querySelector('[data-row=valid] dd').textContent);
  ok(!/(now|adesso)/.test(box.querySelector('[data-row=test] dd').textContent) && /\d/.test(box.querySelector('[data-row=test] dd').textContent),'the driving test is a month after the issue: '+box.querySelector('[data-row=test] dd').textContent);
  ok(/^(0 of 6 hours|0 ore su 6)$/.test(box.querySelector('[data-row=lessons] dd').textContent) && box.querySelectorAll('.foglio-lessons input[type=checkbox]').length===3,'three lesson blocks, none done');
  const cb=box.querySelectorAll('.foglio-lessons input')[1]; cb.checked=true; cb.dispatchEvent(new w.Event('change',{bubbles:true}));
  box=$('exam-date-box');
  ok(/^(2 of 6 hours|2 ore su 6)$/.test(box.querySelector('[data-row=lessons] dd').textContent) && box.querySelectorAll('.foglio-lessons input')[1].checked,'ticking a block counts its 2 hours');
  ok(JSON.parse(w.localStorage.getItem('patente_foglio_rosa')).les[1]===true,'the tick is stored');
  const b=w.buildProgressBundle(); ok(b.settings && typeof b.settings.foglioRosa==='string','the foglio rosa travels with sync');
  box.querySelector('[data-ed=frchange]').click(); box=$('exam-date-box');
  ok(box.querySelector('input[data-fr=iss]').value===key(0),'Change the dates reopens the form with the stored dates');
  box.querySelector('input[data-fr=iss]').value=key(-40); box.querySelector('[data-ed=frsave]').click(); box=$('exam-date-box');
  ok(/(now|adesso)/.test(box.querySelector('[data-row=test] dd').textContent) && JSON.parse(w.localStorage.getItem('patente_foglio_rosa')).les[1]===true,'issued over a month ago: the test is possible now, and the ticks survive the change');
  console.log(fails?fails+' FAILED':'all passed'); process.exit(fails?1:0);
},1500);
