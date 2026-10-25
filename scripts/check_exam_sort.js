// Past Results sorts by any column (maintainer, 2026-10-02): a tap on a heading orders by it, a second tap reverses; the page opens newest first; a mock with no time sorts last either way; a row still opens its own exam. Run: node scripts/check_exam_sort.js (UILANG=it-IT).
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
  const qs=w.eval('questions'); const items=[]; for(const q of qs){for(const st of q.statements){items.push({id:q.id,n:String(st.number),chosen:st.answer,s:10}); if(items.length>=30)break;} if(items.length>=30)break;}
  // newest first in storage: wrong 2, 0, 5, 1; times 500, none, 300, 700
  const wr=[2,0,5,1], tm=[500,null,300,700];
  const hist=wr.map((x,i)=>({date:new Date(Date.UTC(2026,9,2,18)-i*86400e3).toISOString(),correct:30-x,total:30,wrong:x,pass:x<=3,level:3,time:tm[i]==null?undefined:tm[i],items}));
  w.localStorage.setItem('patente_exam_history',JSON.stringify(hist));
  w.document.querySelector('.nav-btn[data-screen="exam"]').click();
  const table=w.document.getElementById('exam-history-table');
  const col=i=>[...table.querySelectorAll('tbody tr')].map(r=>r.children[i].textContent.trim());
  const idx=()=>[...table.querySelectorAll('tbody tr')].map(r=>+r.dataset.idx);
  const tap=k=>table.querySelector(`.exam-sort[data-sort="${k}"]`).click();
  const sorted=()=>table.querySelector('th[aria-sort]');
  ok(table.querySelectorAll('thead .exam-sort').length===5,'five sortable headings');
  ok(idx().join()==='0,1,2,3' && sorted().getAttribute('aria-sort')==='descending' && sorted().querySelector('.exam-sort').dataset.sort==='date','opens newest first, marked on the date column');
  tap('date'); ok(idx().join()==='3,2,1,0' && sorted().getAttribute('aria-sort')==='ascending','a second tap on the date: oldest first');
  tap('score'); ok(col(1).join()==='30/30,29/30,28/30,25/30','score: best first: '+col(1).join(' '));
  tap('score'); ok(col(1).join()==='25/30,28/30,29/30,30/30','score again: worst first');
  tap('wrong'); ok(col(2).join()==='5,2,1,0','wrong: most first'); tap('wrong'); ok(col(2).join()==='0,1,2,5','wrong again: fewest first');
  tap('time'); ok(col(3).join()==='11:40,8:20,5:00,\u2013','time: longest first, the untimed mock last: '+col(3).join(' '));
  tap('time'); ok(col(3).join()==='5:00,8:20,11:40,\u2013','time again: shortest first, the untimed mock still last');
  tap('result'); ok(idx()[3]===2,'result: passes first, the fail last'); tap('result'); ok(idx()[0]===2,'result again: the fail first');
  ok(table.querySelectorAll('.exam-sort-dir').length===1 && table.querySelectorAll('tfoot tr').length===2,'one arrow, and the two closing rows stay at the foot');
  table.querySelector('tbody tr').click(); const panel=w.document.getElementById('exam-history-review');
  ok(!panel.classList.contains('hidden') && panel.dataset.idx==='2','a sorted row opens its own exam (the stored index, not the row position)');
  // The open row is highlighted (20261008c), and only while its exam is open.
  const lit=()=>[...table.querySelectorAll('tbody tr.is-open')].map(r=>+r.dataset.idx);
  ok(lit().join()==='2','the row whose exam is open is highlighted');
  table.querySelectorAll('tbody tr')[1].click(); ok(lit().length===1 && lit()[0]===+table.querySelectorAll('tbody tr')[1].dataset.idx,'opening another row moves the highlight');
  table.querySelectorAll('tbody tr')[1].click(); ok(lit().length===0 && panel.classList.contains('hidden'),'a second tap closes the exam and clears the highlight');
  table.querySelector('tbody tr').click(); w.document.getElementById('exam-hist-rev-close').click(); ok(lit().length===0,'Hide clears the highlight too');
  w.updateExamAvailability(); ok(idx()[0]===2,'the order survives a redraw');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
