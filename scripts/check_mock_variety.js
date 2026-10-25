// Variety across mocks (maintainer, 2026-10-03): the composition stays one statement per topic plus five from the safety topics, but no statement, and no statement with the same wording, met in the last 20 mocks is drawn again. Simulates 30 mocks. Run: node scripts/check_mock_variety.js (SRC= another build to compare).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US';
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.localStorage.setItem('patente_level','3');
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{}; w.Element.prototype.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  const qs=w.eval('questions'); const T=new Map(), txt=new Map();
  const key=st=>String(st.italian_text||'').toLowerCase().replace(/[^a-zàèéìòù0-9]+/g,' ').trim();
  for(const q of qs) for(const st of q.statements){ T.set(String(st.number),q.topic); txt.set(String(st.number),key(st)); }
  const SAFE=w.eval('SAFETY_TOPICS'); const topics=new Set(qs.map(q=>q.topic));
  w.localStorage.setItem('patente_exam_history','[]');
  let ruleOk=true, sheets=[];
  for(let m=0;m<30;m++){
    const items=w.buildExamItems(); const ns=items.map(it=>String(it.stmt.number)); sheets.push(ns);
    const c=new Map(); ns.forEach(n=>c.set(T.get(n),(c.get(T.get(n))||0)+1));
    const twice=[...c].filter(([,v])=>v===2);
    ruleOk = ruleOk && ns.length===30 && new Set(ns).size===30 && c.size===topics.size && [...c.values()].every(v=>v<=2) && twice.length===5 && twice.every(([k])=>SAFE.has(k));
    const h=JSON.parse(w.localStorage.getItem('patente_exam_history'));
    h.unshift({date:new Date(Date.UTC(2026,9,3,8)+m*1800e3).toISOString(),correct:28,total:30,wrong:2,pass:true,level:3,items:items.map(it=>({id:it.q.id,n:String(it.stmt.number),chosen:it.stmt.answer}))});
    w.localStorage.setItem('patente_exam_history',JSON.stringify(h));
  }
  ok(ruleOk,'all 30 mocks keep the composition: 30 different statements, every topic, five safety topics twice');
  let rep=0, repText=0;
  for(let m=1;m<30;m++){ const prevN=new Set(sheets.slice(Math.max(0,m-20),m).flat()); const prevT=new Set([...prevN].map(n=>txt.get(n)));
    rep+=sheets[m].filter(n=>prevN.has(n)).length; repText+=sheets[m].filter(n=>prevT.has(txt.get(n))).length; }
  ok(rep===0,'no statement repeats within any 20 consecutive mocks ('+rep+' repeats)');
  ok(repText===0,'nor does the same wording under another number ('+repText+')');
  const after=new Set(sheets.slice(0,1).flat()); const back=sheets.slice(21).flat().filter(n=>after.has(n)).length;
  console.log('     (statements from mock 1 drawn again in mocks 22 to 30: '+back+'; they are free again after twenty)');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
