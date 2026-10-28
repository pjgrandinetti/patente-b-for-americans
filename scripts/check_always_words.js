// Words marked `always` in vocabulary.json are listed in "Words in this question" even when common and never looked up
// (20261028z, maintainer, 2026-10-28: alcuni was missing under a statement that turns on it). Run: node scripts/check_always_words.js
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:'en-US'}); Object.defineProperty(w.navigator,'languages',{value:['en-US']});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  const words=t=>w.lookedUpWordsIn(t).map(x=>x.term+' = '+x.en);
  const a=words('I contrassegni rappresentati in figura sono applicati ad alcuni autobus');
  ok(a.some(x=>/^alcuni = some$/.test(x)),'the plural alcuni is listed with no look-up: '+a.join(' | '));
  const b=words('Nell\'incrocio rappresentato in figura il veicolo B non deve dare la precedenza ad alcun veicolo');
  ok(b.some(x=>/alcun/.test(x.split(' = ')[0]) && /\bany\b/.test(x)),'the singular after non is listed: '+b.join(' | '));
  // A removed alcuni is still listed (20261029a): the maintainer had removed it from his study list.
  w.localStorage.setItem('patente-lookups', JSON.stringify({alcuni:{term:'alcuni',en:'some',t:1,d:2}}));
  const lk=w.lookupsLog ? w.lookupsLog() : {}; const removedSeen=lk.alcuni && lk.alcuni.d>lk.alcuni.t;
  const a2=words('I contrassegni rappresentati in figura sono applicati ad alcuni autobus');
  ok(removedSeen && a2.some(x=>/^alcuni = some$/.test(x)),'listed even when removed from the study list, with the dictionary gloss: '+a2.join(' | '));
  // Any removed study-list word is listed too (20261029b).
  w.localStorage.setItem('patente-lookups', JSON.stringify({autobus:{term:'autobus',en:'bus',t:1,d:2}}));
  const a3=words('I contrassegni rappresentati in figura sono applicati ad alcuni autobus');
  ok(a3.some(x=>/^autobus = /.test(x)),'a removed study-list word is listed: '+a3.join(' | '));
  w.localStorage.removeItem('patente-lookups');
  const c=words('Il veicolo deve essere fermato sulla strada');
  ok(!c.some(x=>/^(veicolo|strada) =/.test(x)),'a common word not marked always is still left out: '+c.join(' | '));
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
