// The daily review moves through its pool (20261016f, maintainer, 2026-10-16: on the second day the review began
// again with the questions done the day before). A question never reviewed comes before one reviewed yesterday,
// whatever their miss counts; among equally old questions the most-missed still comes first; an open weak spot
// still leads. Run: node scripts/check_review_order.js (UILANG=it-IT; SRC= another public_html).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US';
const bank=JSON.parse(fs.readFileSync(root+'/questions.json','utf8')).filter(q=>(q.statements||[]).some(s=>!s.retired));
const live=q=>q.statements.filter(s=>!s.retired);
const key=n=>{const d=new Date(); d.setDate(d.getDate()+n); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
// 30 questions missed in Italian and still due. The 20 MOST missed (misses 6) were reviewed yesterday (rv) and
// answered right then (dd); the 10 least missed (misses 3) have never been reviewed. One open weak spot, reviewed yesterday too.
const L={1:{},2:{},3:{}}; const cards=bank.slice(0,31);
cards.forEach((q,i)=>{ const st=live(q)[0]; const full={}; q.statements.forEach(s=>{full[s.number]={seen:1,correct:1,streak:1,given:s.answer};});
  for(const l of [1,2,3]) L[l][q.id]={lastSeen:'2026-09-01T00:00:00.000Z',st:JSON.parse(JSON.stringify(full))};
  if(i<20) L[3][q.id].st[st.number]={seen:8,correct:2,streak:2,miss:6,given:st.answer,rv:key(-1),dd:key(-1),dr:1};
  else if(i<30) L[3][q.id].st[st.number]={seen:5,correct:2,streak:2,miss:3,given:st.answer};
  else L[3][q.id].st[st.number]={seen:2,correct:1,streak:0,miss:1,rv:key(-1)}; });
const W=cards[30];
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.localStorage.setItem('patente_level','3'); for (const l of [1,2,3]) w.localStorage.setItem('patente_progress_L'+l, JSON.stringify(L[l]));
w.localStorage.setItem('patente_exam_date',key(9));
const good=[1,0,1,1,0,2,1,0,1,1,0,1,1,0,1];
w.localStorage.setItem('patente_exam_history',JSON.stringify(good.map((x,i)=>{const d=new Date(); d.setDate(d.getDate()-2-i); return {date:d.toISOString(),correct:30-x,total:30,wrong:x,pass:true,level:3,items:[]};})));
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollTo=function(){}; w.Element.prototype.scrollIntoView=function(){}; w.alert=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  w.reviewPerDay=()=>20; w.italianoComplete=()=>true; w.renderDashboard();
  const pool=w.dailyReviewPool(), set=w.dailyReviewSet();
  const fresh=new Set(cards.slice(20,30).map(q=>q.id)), old=new Set(cards.slice(0,20).map(q=>q.id));
  ok(pool.length===31,'31 questions are due: '+pool.length);
  ok(set[0].id===W.id,'the open weak spot still comes first');
  ok(set.slice(1,11).every(x=>fresh.has(x.id)),'then the 10 never reviewed, although they were missed less');
  ok(set.slice(11).every(x=>old.has(x.id)),'the questions reviewed yesterday come after them');
  ok(pool.slice(11).every((x,i,a)=>i===0||a[i-1].total>=x.total),'among those, the most-missed first');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
