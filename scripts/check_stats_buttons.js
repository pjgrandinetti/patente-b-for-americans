// Statistics: "Take another mock exam" and "Clear all results" stay right under the Past Results table when a past exam is opened (maintainer, 2026-10-02). STALE=1 puts the review panel first in index.html, as an older cached page has it. Run: node scripts/check_stats_buttons.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US';
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
if(process.env.STALE) html=html.replace(/(\s*<div class="exam-history-actions">[\s\S]*?<\/div>)(\s*<div id="exam-history-review" class="exam-review hidden"><\/div>)/,'$2$1');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.localStorage.setItem('patente_level','3');
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{}; w.Element.prototype.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const $=id=>w.document.getElementById(id);
setTimeout(()=>{
  const qs=w.eval('questions'); const items=[];
  for(const q of qs){for(const st of q.statements||[]){items.push({id:q.id,number:st.number,given:st.answer,correct:st.answer,ok:true}); if(items.length>=30)break;} if(items.length>=30)break;}
  const hist=[0,1].map(i=>({date:new Date(Date.UTC(2026,9,1,18)-i*3600e3).toISOString(),correct:30,total:30,wrong:0,pass:true,level:3,time:500,items}));
  w.localStorage.setItem('patente_exam_history',JSON.stringify(hist));
  w.document.querySelector('.nav-btn[data-screen="exam"]').click();
  const table=$('exam-history-table'), actions=w.document.querySelector('.exam-history-actions');
  const under=()=>table.nextElementSibling===actions;
  ok(under() && actions.contains($('btn-clear-exam-history')),'Clear all results right under the table');
  ok($('stats-mock-row').contains($('btn-stats-mock')) && $('stats-mock-row').nextElementSibling===$('exam-history') && !$('exam-history-box').contains($('btn-stats-mock')),'Take another mock exam in its own row above the ring, outside the past-results box');
  table.querySelector('tr[data-idx]').click();
  const panel=$('exam-history-review');
  ok(!panel.classList.contains('hidden') && panel.innerHTML.length>0,'a past exam opens');
  ok(under(),'with a past exam open the buttons are still right under the table');
  ok(actions.compareDocumentPosition(panel)&w.Node.DOCUMENT_POSITION_FOLLOWING,'the opened exam is below the buttons');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
