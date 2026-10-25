// The Weak spots drill prints how many times each statement has been missed,
// every level and the mocks together, and marks it at DRILL_ATTENTION or more.
// Run: node scripts/check_drill_misses.js (UILANG=it-IT; SRC=; JSDOM=).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:process.env.UILANG||'en-US'}); Object.defineProperty(w.navigator,'languages',{value:[process.env.UILANG||'en-US']});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}}); w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}};
const qs=JSON.parse(fs.readFileSync(root+'/questions.json','utf8'));
const find=n=>{for(const q of qs)for(const s of q.statements)if(s.number===n)return q;};
const card=find('22927'); // 22927..22936
const mk=m=>({seen:1+m,correct:1,streak:0,miss:m});
const P={1:{},2:{},3:{}};
P[1][card.id]={st:{'22934':mk(1),'22935':mk(1)}};
P[2][card.id]={st:{'22934':mk(1)}};
P[3][card.id]={st:{'22934':mk(2),'22935':{seen:1,correct:0,streak:0,miss:1},'22936':{seen:3,correct:1,streak:1,lft:1}}};
for(const L of [1,2,3]) w.localStorage.setItem('patente_progress_L'+L,JSON.stringify(P[L]));
w.localStorage.setItem('patente_level','3');
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  try{ w.eval("setLevel(3)"); }catch{}
  w.document.querySelector('[data-screen="exam"]')?.click();
  w.eval('startDrill()');
  const badges=[...w.document.querySelectorAll('.stmt-miss-count')];
  const by=n=>{const li=[...w.document.querySelectorAll('#card-statements li')].find(l=>l.querySelector('.stmt-number')?.textContent==='#'+n); return li&&li.querySelector('.stmt-miss-count');};
  ok(w.eval('session.buildMode')==='drill','the drill started');
  ok(by('22934') && /4/.test(by('22934').textContent) && by('22934').classList.contains('stmt-miss-hot') && by('22934').textContent.startsWith('⚠️'),'22934: four misses over three levels, warning mark: '+(by('22934')&&by('22934').textContent));
  ok(by('22935') && /2/.test(by('22935').textContent) && !by('22935').classList.contains('stmt-miss-hot') && !by('22935').textContent.includes('⚠️'),'22935: two misses, no mark: '+(by('22935')&&by('22935').textContent));
  ok(!by('22927'),'a statement not in the drill carries no count');
  ok(w.eval("missTotal('"+card.id+"','22936')")===0,'a credit-only record counts nothing');
  ok(w.eval("t('drill.missedOne')").length>0,'the singular string exists');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
