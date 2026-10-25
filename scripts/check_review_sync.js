// The daily review across two devices (20261011c, maintainer, 2026-10-04: "Start the Review is not syncing"). Answers given in the review on one device count on the other: the day's set there is smaller by as many, and those questions are not offered again today. Run: node scripts/check_review_sync.js
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const bank=JSON.parse(fs.readFileSync(root+'/questions.json','utf8')).filter(q=>(q.statements||[]).some(s=>!s.retired));
const live=q=>q.statements.filter(s=>!s.retired);
const key=n=>{const d=new Date(); d.setDate(d.getDate()+n); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
const L={1:{},2:{},3:{}}; const cards=bank.slice(0,40);
cards.forEach(q=>{ const full={}; q.statements.forEach(s=>{full[s.number]={seen:1,correct:1,streak:1,given:s.answer};});
  for(const l of [1,2,3]) L[l][q.id]={lastSeen:'2026-09-01T00:00:00.000Z',st:JSON.parse(JSON.stringify(full))};
  const st=live(q)[0]; L[3][q.id].st[st.number]={seen:5,correct:2,streak:2,miss:3,given:st.answer}; });
const html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const good=[1,0,1,1,0,2,1,0,1,1,0,1,1,0,1];
function boot(){
  const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true}); const w=dom.window;
  w.localStorage.setItem('patente_level','3'); for(const l of [1,2,3]) w.localStorage.setItem('patente_progress_L'+l,JSON.stringify(L[l]));
  w.localStorage.setItem('patente_exam_date',key(9));
  w.localStorage.setItem('patente_exam_history',JSON.stringify(good.map((x,i)=>{const d=new Date(); d.setDate(d.getDate()-1-i); return {date:d.toISOString(),correct:30-x,total:30,wrong:x,pass:true,level:3,items:[]};})));
  w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
  w.scrollTo=()=>{}; w.Element.prototype.scrollTo=function(){}; w.Element.prototype.scrollIntoView=function(){}; w.alert=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
  w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
  const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s); return w;
}
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const A=boot(), B=boot();
setTimeout(()=>{
  for (const w of [A,B]) { w.italianoComplete=()=>true; w.reviewPerDay=()=>20; }
  ok(A.dailyReviewSet().length===20 && B.dailyReviewSet().length===20,'both devices start with 20 to review');
  A.startDailyReview();
  const done=[];
  for (let k=0;k<3;k++){ const li=A.document.querySelector('#card-statements .statement-item'); const se=A.eval('session'); done.push(se.queue[se.index]+':'+li.dataset.number);
    li.querySelector(li.dataset.answer==='VERO'?'.btn-vero':'.btn-falso').click(); A.document.getElementById('btn-next').click(); }
  ok(A.reviewDoneToday()===3 && A.dailyReviewSet().length===17,'A answered 3: 17 left on A');
  B.mergeDeviceState(JSON.parse(JSON.stringify(A.buildProgressBundle())));
  B.mergeProgressData && B.mergeProgressData(JSON.parse(JSON.stringify(A.buildProgressBundle())));
  ok(B.reviewDoneToday()===3,'after a sync B counts the 3 answered on A: '+B.reviewDoneToday());
  const bset=B.dailyReviewSet().map(x=>x.id+':'+x.num);
  ok(bset.length===17 && !done.some(d=>bset.includes(d)),'B offers the 17 left, none of the three A answered');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},3000);
