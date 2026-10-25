// The Reference vocabulary search (20261007n, reported 2026-10-01: "sull'impresa assicuratrice" found nothing). Asserts the recorded cases and then sweeps the bank: phrases of 2 to 4 words cut from the live statements, every one holding an elided word plus a fixed sample of the rest, must return at least one vocabulary row whenever the app's own gloss highlighter finds an entry inside them. The one known exception is a query made only of function words ("cui la"). Run: node scripts/check_ref_search.js
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; w.localStorage.setItem('patente_level','1');
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}}); w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
const Q=JSON.parse(fs.readFileSync(root+'/questions.json','utf8'));
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  const dict=w.buildTopicVocabMap();
  const items=[...dict.values()].map(e=>({term:e.term,en:e.en}));
  const search=q=>w.refFilterRank(items, w.refNeedles(q), (i,n)=>w.vocabMatches(i,n), i=>i.term).map(i=>i.term);
  const first=q=>search(q)[0];
  ok(first("sull'impresa assicuratrice")==='impresa assicuratrice','sull\'impresa assicuratrice: impresa assicuratrice first ('+search("sull'impresa assicuratrice").slice(0,3).join(', ')+')');
  ok(first("sull’impresa assicuratrice")==='impresa assicuratrice','the same with a typographic apostrophe');
  ok(search("nell'ordine:").includes('ordine') || search("nell'ordine:").length>0,'a colon glued to the word: '+search("nell'ordine:").slice(0,3).join(', '));
  ok(search('di 70 km/h').some(t=>/km\/h/.test(t)),'km/h keeps its slash');
  ok(search("E' regolamentare").includes("e' regolamentare"),"E' keeps its apostrophe (the bank's spelling of è)");
  ok(search('in cui è').includes('in cui'),'a two-word entry of function words (in cui)');
  ok(search('Nelle aree pedonali').some(t=>/area pedonale/.test(t)),'a four-letter inflection (aree, area pedonale)');
  const long=search("per l'accesso dei veicoli alle proprietà laterali");
  ok(long.length===5 && ['veicolo','laterale','accesso','proprietà','proprietà laterali'].every(t=>long.includes(t)),'the recorded long query still returns its five rows: '+long.join(', '));
  ok(search('poligono di tiro').some(t=>/poligono di tiro a segno/.test(t)),'poligono di tiro still finds the longer entry');
  ok(search('veicoli').length>=100,'a single word still browses ('+search('veicoli').length+' rows)');
  // The Glossario reads the same splitter: the recorded long query keeps its one row.
  const G=JSON.parse(fs.readFileSync(root+'/glossary.json','utf8')).entries;
  const gsearch=q=>w.refFilterRank(G, w.refNeedles(q), (e,n)=>w.glossWords(e.t).some(x=>x.startsWith(n)) || w.glossFold(e.d).includes(n), e=>e.t).map(e=>e.t);
  const gl=gsearch("per l'accesso dei veicoli alle proprietà laterali");
  ok(gl.length===1,'Glossario, the long query: one row ('+gl.join(', ')+')');
  ok(gsearch("sull'impresa assicuratrice").length>=0,'Glossario does not break on the new needles');
  // the sweep
  const oracle=q=>{ const h=w.highlightVocabInEscaped(w.escHtml(q), dict, false); return /data-term=/.test(h); };
  let seed=7; const rnd=()=>{ seed=(seed*1103515245+12345)%2147483648; return seed/2147483648; };
  let tried=0; const bad=[];
  for (const c of Q) for (const st of c.statements) { if (st.retired) continue; const toks=st.italian_text.split(/\s+/);
    for (let i=0;i<toks.length;i++) for (let n=2;n<=4;n++) { if (i+n>toks.length) break; const q=toks.slice(i,i+n).join(' ');
      if (!(/'/.test(toks[i]) || rnd()<0.004) || !oracle(q)) continue; tried++; if (!search(q).length) bad.push(q); } }
  const known=bad.filter(q=>q.split(/\s+/).every(t=>w.eval('refStop')(t.replace(/[^\p{L}']/gu,''))));
  ok(bad.length===known.length,'sweep: '+tried+' bank phrases holding an entry, '+(bad.length-known.length)+' found nothing'+(bad.length>known.length?': '+bad.filter(q=>!known.includes(q)).slice(0,8).join(' | '):'')+(known.length?' (plus '+known.length+' made only of function words)':''));
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
