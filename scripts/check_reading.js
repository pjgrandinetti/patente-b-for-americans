// A statement's `reading` (maintainer, 2026-10-02, flag 31036): the Italian sentence in labelled parts, drawn after the English explanation wherever it shows, for a non-Italian browser only. Run: node scripts/check_reading.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US'; const IT=LANG.startsWith('it');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{}; w.Element.prototype.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const NUM='31036';
setTimeout(()=>{
  const q=w.eval('questions').find(q=>q.statements.some(s=>String(s.number)===NUM)); const st=q.statements.find(s=>String(s.number)===NUM);
  const li=()=>[...w.document.querySelectorAll('#card-statements li')].find(l=>l.textContent.includes(NUM));
  const answer=(lvl,right)=>{ w.localStorage.clear(); w.eval('progress={}'); w.setLevel(lvl); w.eval('progress={}'); w.openCardFromSearch(q.id,NUM);
    const want=right?st.answer:(st.answer==='VERO'?'FALSO':'VERO'); li().querySelector(want==='VERO'?'.btn-vero':'.btn-falso').click(); return li(); };
  const rows=el=>[...el.querySelectorAll('.stmt-reading .gr-parse-row')].map(r=>[r.querySelector('.gr-parse-lab').textContent,r.querySelector('.gr-exit').textContent,r.querySelector('.gr-parse-en').textContent]);
  if(IT){
    const l=answer(3,false);
    ok(!l.querySelector('.stmt-reading'),'an Italian browser sees no part-by-part reading');
    ok(!/Reading the Italian/.test(st.explanation),'the prose reading is gone from the explanation');
    console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
  }
  let l=answer(1,false); let r=rows(l);
  ok(r.length===4 && l.querySelector('.stmt-explanation .stmt-reading'),'English level: four labelled parts under the explanation');
  ok(r.map(x=>x[1]).join(' ')===st.italian_text,'the Italian parts join to the statement');
  ok(l.querySelectorAll('.stmt-reading .gr-parse-main').length===1 && l.querySelector('.gr-parse-main .gr-exit').textContent==='ci si espone','the main verb row is ci si espone');
  ok(r[1][2]==='one exposes oneself' && r[0][0]==='When','each part has a label and its English: '+r.map(x=>x[0]+' / '+x[2]).join(' | '));
  const note=l.querySelector('.stmt-reading-note');
  ok(note && note.querySelectorAll('i').length>=4 && !/\*/.test(note.textContent) && /esporsi/.test(note.textContent),'a note names the forms, in italics: '+note.textContent.slice(0,80));
  ok(!/Reading the Italian/.test(l.textContent),'the prose reading is gone from the explanation');
  l=answer(2,false); ok(l.querySelector('.stmt-english-expl .stmt-reading') && !l.querySelector('.stmt-explanation > .stmt-reading'),'hint level: the reading sits with the English explanation, not the Italian one');
  l=answer(3,false); ok(l.querySelector('.stmt-english-expl .stmt-reading') && l.querySelectorAll('.stmt-reading').length===1,'Italian only, wrong answer: the reading follows the English explanation, once');
  l=answer(3,true); ok(!l.querySelector('.stmt-reading') || l.querySelector('.stmt-expl-box').classList.contains('hidden'),'Italian only, right answer: nothing shows until Why? is asked');
  const sib=q.statements.find(s=>!s.reading); ok(w.readingHtml(sib)==='','a statement without the field shows nothing');
  const rev=w.buildExamReviewHtml([{q,stmt:st,chosen:'FALSO',correct:false}]);
  ok(/stmt-reading/.test(rev) && (rev.match(/stmt-reading-head/g)||[]).length===1,'the mock review carries it once');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
