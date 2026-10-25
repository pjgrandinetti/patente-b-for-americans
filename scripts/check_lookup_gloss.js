const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:'en-US'});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}}); w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}};
// seed: rows as the old logLookup wrote them (whole tooltip in en)
const now=Date.now();
w.localStorage.setItem('patente-lookups',JSON.stringify({
  'sopraggiungano':{term:'sopraggiungano',en:'(they) approach / come up\nsopraggiungere · congiuntivo presente · 3rd pl. · irreg.',t:now},
  'fosse':{term:'fosse',en:'were\nessere · congiuntivo imperfetto · 3rd sing.',t:now},
  'giunti in prossimità di un incrocio':{term:'giunti in prossimità di un incrocio',en:'once you are close to an intersection',t:now},
}));
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  w.eval("vocabTab='every'");
  const box=w.document.getElementById('review-search'); box.value='giunti'; box.dispatchEvent(new w.Event('input',{bubbles:true}));
  w.eval('renderVocabScreen()');
  const terms=[...w.document.querySelectorAll('#vocab-body li')].map(li=>li.querySelector('.lookups-term').textContent);
  ok(!terms.includes('sopraggiungano'),'a subjunctive verb no longer matches *giunti* through "congiuntivo"');
  ok(!terms.includes('fosse'),'fosse does not match either');
  ok(terms.includes('giunti in prossimità di un incrocio'),'the phrase that contains the word still matches');
  ok(terms.length===4,'four rows in all, got '+terms.length+': '+terms.join(', '));
  box.value=''; box.dispatchEvent(new w.Event('input',{bubbles:true})); w.eval("vocabTab='study'"); w.eval('renderVocabScreen()');
  const li=[...w.document.querySelectorAll('#vocab-body li')].find(l=>l.querySelector('.lookups-term').textContent==='sopraggiungano');
  const gloss=li&&li.querySelector('.lookups-gloss').childNodes[0].textContent;
  ok(gloss==='(they) approach / come up','study-list row shows the gloss alone: '+JSON.stringify(gloss));
  ok(li&&li.querySelector('.lookups-gram').textContent.includes('congiuntivo'),'and the grammar line once, in its own span');
  const stored=JSON.parse(w.localStorage.getItem('patente-lookups'));
  ok(!Object.values(stored).some(r=>r.en.includes('\n')),'stored rows migrated: no grammar line left in en');
  // a fresh look-up writes the gloss alone
  const span=w.document.createElement('span'); span.className='vocab-term'; span.setAttribute('data-term','vietino'); span.setAttribute('data-tooltip','(they) prohibit\nvietare · congiuntivo presente · 3rd pl.');
  w.eval('logLookup')(span);
  ok(JSON.parse(w.localStorage.getItem('patente-lookups')).vietino.en==='(they) prohibit','a new look-up stores the gloss alone');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
