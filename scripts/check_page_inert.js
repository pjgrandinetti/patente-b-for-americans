// The page beneath an open overlay is inert (20261031i, maintainer, 2026-10-31: the browser's find-in-page
// searched the page under the notes). Run: node scripts/check_page_inert.js (UILANG=it-IT; SRC= another public_html).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US';
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollTo=function(){}; w.Element.prototype.scrollIntoView=function(){}; w.alert=()=>{};
w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const $=id=>w.document.getElementById(id);
const page=()=>[...w.document.querySelectorAll('#nav, section.screen')];
setTimeout(()=>{
  ok(page().length===6 && page().every(e=>!e.hasAttribute('inert')),'nothing is inert with no overlay open');
  w.openReview(w.eval('questions[0].topic'));
  ok(!$('review-overlay').classList.contains('hidden') && page().every(e=>e.hasAttribute('inert')) && !$('review-overlay').hasAttribute('inert'),'with the notes open, the nav and every screen are inert and the overlay is not');
  w.openSettings();
  w.closeSettings();
  ok(page().every(e=>e.hasAttribute('inert')),'a second overlay opened and closed over the notes leaves the page inert');
  w.dismissReview();
  ok($('review-overlay').classList.contains('hidden') && page().every(e=>!e.hasAttribute('inert')),'closing the notes makes the page live again');
  console.log(fails?fails+' FAILED':'all passed'); process.exit(fails?1:0);
},1500);
