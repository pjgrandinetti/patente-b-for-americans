// Look-up ENCOUNTERS are counted per word (n, and the stamps in h), the
// count survives a removal and a sync merge, and a wrong answer at Solo
// italiano names the statement's looked-up words under the English.
// Run: node scripts/check_lookup_count.js (UILANG=it-IT; SRC=; JSDOM=).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US';
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}}); w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}};
const qs=JSON.parse(fs.readFileSync(root+'/questions.json','utf8'));
const find=n=>{for(const q of qs)for(const s of q.statements)if(s.number===n)return {q,s};};
const {q:card,s:stmt}=find('18465'); // "La carreggiata è la parte della strada destinata ..."
const now=Date.now(), H=3600e3;
// carreggiata: looked up long ago, in the list; strada: removed (d > t)
w.localStorage.setItem('patente-lookups',JSON.stringify({
  'carreggiata':{term:'carreggiata',en:'roadway / carriageway',t:now-5*H,n:2,h:[now-30*H,now-5*H]},
  'strada':{term:'strada',en:'road',t:now-9*H,d:now-8*H,rc:1,rct:now-8*H},
}));
w.localStorage.setItem('patente_level','3');
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const log=()=>JSON.parse(w.localStorage.getItem('patente-lookups'));
const tap=(term,tt)=>{const sp=w.document.createElement('span'); sp.className='vocab-term'; sp.setAttribute('data-term',term); sp.setAttribute('data-tooltip',tt||'x'); w.eval('logLookup')(sp);};
setTimeout(()=>{
  // 1. counting
  tap('carreggiata','roadway / carriageway');
  ok(log().carreggiata.n===3 && log().carreggiata.h.length===3,'a look-up five hours after the last one is a new encounter: n=3');
  tap('carreggiata','roadway / carriageway');
  ok(log().carreggiata.n===3,'a second tap within the gap is the same encounter: still 3');
  tap('strada','road');
  ok(log().strada.n===1 && (log().strada.d||0)>(log().strada.t||0),'a REMOVED word still counts its encounter, and stays removed');
  tap('sosta','parking');
  ok(log().sosta.n===1 && log().sosta.h.length===1,'a first look-up starts at n=1');
  // 2. the merge keeps the larger count and unions the histories
  const mine=log(); const theirs={carreggiata:{term:'carreggiata',en:'roadway / carriageway',t:now-2*H,n:5,h:[now-50*H,now-2*H]}};
  w.eval('mergeLookups')(theirs,0);
  const m=log().carreggiata;
  ok(m.n===5,'merge takes the larger encounter count: '+m.n);
  ok(m.h.length===5 && m.h[0]===now-50*H,'merge unions the histories, oldest first: '+m.h.length);
  // history cap
  const big={x:{term:'x',en:'y',t:now,n:99,h:Array.from({length:40},(_,i)=>now-(40-i)*H)}};
  w.eval('mergeLookups')(big,0);
  ok(log().x.h.length===w.eval('LOOKUP_HISTORY'),'history capped at LOOKUP_HISTORY');
  // 3. the words named under a wrong answer at L3
  try{ w.eval("setLevel(3)"); }catch{}
  w.eval('startStudySession')('topic',card.topic);
  // jump to the card that holds 18465
  const idx=w.eval('session.queue').indexOf(card.id);
  w.eval('session.index='+idx+'; renderStudyCard()');
  const li=[...w.document.querySelectorAll('#card-statements li')].find(l=>l.querySelector('.stmt-number')?.textContent==='#18465');
  ok(!!li,'the card with 18465 is on screen');
  const wrong=stmt.answer==='VERO'?'.btn-falso':'.btn-vero';
  li.querySelector(wrong).click();
  const box=li.querySelector('.stmt-lookedup');
  if(LANG.startsWith('it')){
    ok(!box,'an Italian browser sees no looked-up line');
  } else {
    ok(!!box,'a wrong answer at Solo italiano names the looked-up words');
    const txt=box?box.textContent:'';
    ok(/carreggiata/.test(txt) && /roadway/.test(txt),'carreggiata, with its gloss: '+JSON.stringify(txt));
    ok(!/\bstrada\b/.test(txt.replace(/carreggiata/g,'')),'a REMOVED word (strada) is not named');
    ok(!/\bveicol/.test(txt),'a common word never looked up (veicoli) is not named');
    ok(/normalmente/.test(txt),'a RARE word never looked up (normalmente, 3 uses in the bank) IS named');
    ok(!!li.querySelector('.stmt-english-primary'),'the English translation is still there above it');
  }
  // a RIGHT answer names nothing
  const li2=[...w.document.querySelectorAll('#card-statements li')].find(l=>l.querySelector('.stmt-number')?.textContent==='#18466');
  const st2=find('18466').s; li2.querySelector(st2.answer==='VERO'?'.btn-vero':'.btn-falso').click();
  ok(!li2.querySelector('.stmt-lookedup') || li2.querySelector('.stmt-lookedup').classList.contains('hidden'),'a right answer shows no words unasked');
  // Why? on a RIGHT answer: 18462 carries a rare word (suddivisa, never
  // looked up). Answer it right, then press Why?.
  const li4=[...w.document.querySelectorAll('#card-statements li')].find(l=>l.querySelector('.stmt-number')?.textContent==='#18462');
  const st4=find('18462').s; li4.querySelector(st4.answer==='VERO'?'.btn-vero':'.btn-falso').click();
  const why=li4.querySelector('.stmt-why-btn');
  if (LANG.startsWith('it')) {
    ok(!li4.querySelector('.stmt-lookedup'),'an Italian browser sees no words on a right answer either');
  } else {
    ok(!!why,'a right answer offers Why?');
    const wl=li4.querySelector('.stmt-lookedup');
    ok(wl && wl.classList.contains('hidden'),'the words exist but are folded until Why? is pressed');
    why && why.click();
    ok(wl && !wl.classList.contains('hidden') && /suddivisa/.test(wl.textContent),'Why? unfolds them, with the rare word: '+(wl&&wl.textContent));
    why && why.click();
    ok(wl && wl.classList.contains('hidden'),'and folds them again');
  }
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
