// The manifest names the app for install prompts (20261017g, maintainer, 2026-10-17): the English one says the
// app is a Patente B study app written for Americans, an Italian browser is pointed at manifest-it.json, and both
// keep the short name "Patente B" as the home-screen label. Run: node scripts/check_manifest.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US', IT=LANG.startsWith('it');
const en=JSON.parse(fs.readFileSync(root+'/manifest.json','utf8')), it=JSON.parse(fs.readFileSync(root+'/manifest-it.json','utf8'));
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  ok(/for Americans/.test(en.name) && en.short_name==='Patente B','the English manifest names the app for Americans and keeps the short name: '+en.name);
  ok(/patente/i.test(it.name) && !/Americans/.test(it.name) && it.short_name==='Patente B','the Italian manifest is Italian and keeps the short name: '+it.name);
  ok(JSON.stringify(en.icons)===JSON.stringify(it.icons) && en.start_url===it.start_url && en.scope===it.scope,'the two manifests differ only in their wording');
  const href=w.document.querySelector('link[rel="manifest"]').getAttribute('href');
  ok(href===(IT?'manifest-it.json':'manifest.json'),'this face links '+href);
  ok(/for Americans/.test(w.document.title)!==IT,'the tab title matches the face: '+w.document.title);
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},1500);
