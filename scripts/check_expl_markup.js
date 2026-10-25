// Explanations mark an Italian word in *italics* and a phrase in **bold** (20261010h, flag 24611): the app renders both, and no live explanation is left with a literal asterisk once rendered. Run: node scripts/check_expl_markup.js
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true}); const w=dom.window;
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollTo=function(){}; w.Element.prototype.scrollIntoView=function(){}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}}); w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  ok(typeof w.explHtml==='function','explHtml exists');
  ok(w.explHtml('the *revoca* and **from its beginning** <b>')==='the <i>revoca</i> and <strong>from its beginning</strong> &lt;b&gt;','italics, bold, and everything else escaped');
  const qs=w.eval('questions'); const bad=[];
  for (const q of qs) for (const st of q.statements) for (const k of ['explanation','explanation_it']) { const e=st[k]; if (e && w.explHtml(e).includes('*')) bad.push(st.number+' '+k); }
  ok(!bad.length,'no explanation keeps a literal asterisk once rendered'+(bad.length?': '+bad.slice(0,5).join(', '):''));
  const st=qs.flatMap(q=>q.statements).find(x=>String(x.number)==='24611');
  ok(/<i>ritiro<\/i>.*<i>sospensione<\/i>.*<i>revisione<\/i>.*<i>revoca<\/i>/.test(w.explHtml(st.explanation)),'24611 names the four measures in Italian, in italics');
  // Links into the notes (20261010n, flags 18625 and 19088).
  const st2=qs.flatMap(q=>q.statements).find(x=>String(x.number)==='19088');
  const h=w.explHtml(st2.explanation);
  ok(/<a href="#" class="expl-notes" data-img="domandeb_images\/4067.svg">a warning triangle/.test(h) && !/notes:/.test(h),'a [words](notes:figure) link renders as a link, with no markup left');
  const div=w.document.createElement('div'); div.innerHTML=h; w.document.body.appendChild(div);
  div.querySelector('a.expl-notes[data-img$="4067.svg"]').click();
  const ov=w.document.getElementById('review-overlay');
  ok(!ov.classList.contains('hidden') && /Segnali di pericolo/.test(w.eval('reviewTopic')) && ov.querySelector('.review-fig-flash img')?.getAttribute('src')==='domandeb_images/4067.svg','clicking it opens the warning-sign notes at the locomotive triangle');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
