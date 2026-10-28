// How to remember the speeds on the Reference page (20261028l, maintainer, 2026-10-28): the rule topic 11 teaches, shown once,
// closed, at the head of whichever speed category comes first; with the by-vehicle chip alone it still shows; never on another
// category, while searching, or on the missed-figures chip; every figure it names is a speed on the page. Run: node scripts/check_speed_remember.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US'; const IT=LANG.startsWith('it');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  const $=id=>w.document.getElementById(id);
  w.document.querySelector('[data-screen="vocab"]')?.click();
  w.document.querySelector('.review-section-btn[data-section="numbers"]')?.click();
  const chip=id=>{ const c=w.document.querySelector(`.review-chip[data-cat="${id}"]`); if(c) c.click(); return !!c; };
  const rem=()=>[...$('review-numbers-body').querySelectorAll('.ref-remember')];
  chip('all');
  let r=rem().filter(d=>d.dataset.rem==='speed');
  ok(r.length===1 && !r[0].open,'all categories: one speeds disclosure, closed');
  const title=r[0].querySelector('h2,summary').textContent;
  ok(title===(IT?'Come ricordare le velocità':'How to remember the speeds'),'its title: '+title);
  ok(r[0].querySelectorAll('li').length===9,'nine lines');
  const fig=r[0].querySelector('img.ref-remember-fig');
  ok(fig && fig.getAttribute('src')==='review_media/speed-limits-'+(IT?'it':'en')+'.svg' && fs.existsSync(root+'/'+fig.getAttribute('src')) && fig.alt.length>40,'the grid figure in the reader\'s language: '+(fig&&fig.getAttribute('src')));
  const cats=[...$('review-numbers-body').querySelectorAll('.review-cat-title')];
  ok(cats[0] && /(Speeds by road type|Velocità per tipo di strada)/.test(cats[0].textContent) && cats[0].nextElementSibling===r[0],'it sits under the first speed category');
  ok(/(odd tens|decine dispari)/.test(r[0].textContent) && /(100|80)/.test(r[0].textContent),'it teaches the series and the exceptions');
  // A tap opens the figure full screen; Esc closes it and leaves the page as it was (20261028o).
  fig.click();
  const v=$('fig-viewer');
  ok(v && !v.classList.contains('hidden') && v.querySelector('img').getAttribute('src')===fig.getAttribute('src') && w.document.body.classList.contains('fig-viewing'),'a tap opens the figure full screen');
  w.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
  ok(v.classList.contains('hidden') && !w.document.body.classList.contains('fig-viewing') && !$('screen-vocab').classList.contains('hidden'),'Esc closes it and the Reference page stays');
  fig.click(); v.querySelector('.fig-viewer-close').click(); ok(v.classList.contains('hidden'),'the close button closes it');
  fig.click(); ok(/(Pinch|Avvicina)/.test(v.querySelector('.fig-viewer-hint').textContent),'it says how to zoom: '+v.querySelector('.fig-viewer-hint').textContent); w.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
  const ref=JSON.parse(fs.readFileSync(root+'/reference.json','utf8'));
  const speeds=new Set(ref.numbers.filter(n=>n.cat==='speed'||n.cat==='speedveh').map(n=>(String(n.value).match(/\d+/)||[])[0]));
  const named=new Set((r[0].textContent.match(/\b\d+\b/g)||[]).filter(x=>!['3','10','20'].includes(x)));
  ok([...named].every(x=>speeds.has(x)),'every speed it names is a speed on the page: '+[...named].join(' '));
  r[0].open=true; r[0].dispatchEvent(new w.Event('toggle'));
  chip('speedveh'); r=rem();
  ok(r.length===1 && r[0].open,'the by-vehicle chip alone still shows it, and it stays open once opened');
  chip('size'); ok(rem().length===0,'not under another category');
  // The distances carry their own box (20261028q), text only since 20261028r.
  chip('distance'); r=rem();
  ok(r.length===1 && r[0].dataset.rem==='distance' && /(How to remember the distances|Come ricordare le distanze)/.test(r[0].querySelector('summary').textContent) && r[0].querySelectorAll('li').length===8,'the distances have their own box, eight lines');
  ok(!r[0].querySelector('img'),'text only, with no figure (removed in 20261028r)');
  const dvals=new Set(ref.numbers.filter(n=>n.cat==='distance').map(n=>(String(n.value).match(/\d+/)||[])[0]));
  const kmh=new Set(['30','50','100','130','150']);
  const dnamed=(r[0].textContent.match(/\b\d+(?:[.,]\d+)?\b/g)||[]).filter(x=>!['3,5','3.5','10','3'].includes(x)||dvals.has(x));
  ok(dnamed.every(x=>dvals.has(x)||kmh.has(x)),'every distance it names is a distance on the page: '+[...new Set(dnamed)].join(' '));
  chip('all'); ok(rem().length===2,'all categories: the speeds\' box and the distances\' box');
  const box=$('review-search')||w.document.querySelector('input[type=search]');
  if (box){ box.value='130'; box.dispatchEvent(new w.Event('input',{bubbles:true})); }
  ok(rem().length===0,'not while searching');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
