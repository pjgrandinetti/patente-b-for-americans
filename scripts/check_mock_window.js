// Which mocks the readiness figure reads (maintainer, 2026-10-02: no fixed cap of fifteen): every mock on record, unless the scores have clearly changed level, in which case the mocks from before the change are left out; the recent part is never under fifteen; the banner still needs fifteen. Run: node scripts/check_mock_window.js (UILANG=it-IT).
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
const IT=LANG.startsWith('it');
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
// wrongs OLDEST first
const set=wr=>{ const n=wr.length; w.localStorage.setItem('patente_exam_history',JSON.stringify(wr.map((x,i)=>({date:new Date(Date.UTC(2026,9,1,8)+i*1800e3).toISOString(),correct:30-x,total:30,wrong:x,pass:x<=3,level:3,time:540,items:[]})).reverse())); w.updateExamAvailability(); };
setTimeout(()=>{
  const $=id=>w.document.getElementById(id);
  w.document.querySelector('.nav-btn[data-screen="exam"]').click();
  // scipy: binom.cdf(3, 10, 0.5) = 0.171875; binom.cdf(26, 60, 0.75) = 1.7646e-07
  ok(Math.abs(w.binomCdf(3,10,0.5)-0.171875)<1e-9 && Math.abs(w.binomCdf(26,60,0.75)-1.764614889927057e-7)<1e-12 && w.binomCdf(-1,5,.5)===0 && w.binomCdf(5,5,.5)===1,'binomCdf agrees with scipy');
  // The maintainer's eighteen of 2026-10-02: steady, so all eighteen count.
  const his=[0,2,2,4,0,2,3,1,1,2,3,1,1,2,1,1,2,2];
  set(his); let f=w.mockRecentForm();
  ok(f.n===18 && w.mockWindowStart(his)===0,'eighteen steady mocks: all eighteen are used');
  ok(/\b18\b/.test($('exam-readiness-note').textContent) && !/(left out|escluse)/.test($('exam-readiness-note').textContent),'the note says 18 and mentions nothing left out: '+$('exam-readiness-note').textContent);
  // Forty steady mocks: no cap at fifteen.
  const steady=Array.from({length:40},(_,i)=>[1,2,1,0,2,1,3,1,2,1][i%10]); set(steady);
  ok(w.mockRecentForm().n===40,'forty steady mocks: all forty are used, with no cap');
  // A clear change of level: twelve weak mocks, then eighteen good ones.
  const step=[5,4,6,4,5,4,5,6,4,5,4,5, 1,0,1,2,1,0,1,1,0,2,1,1,0,1,1,2,0,1]; set(step); f=w.mockRecentForm();
  ok(w.mockWindowStart(step)===12 && f.n===18,'twelve weak mocks then eighteen good ones: the twelve are left out');
  ok(/\b18\b/.test($('exam-readiness-note').textContent) && /(left out because your scores have changed|escluse perché da allora)/.test($('exam-readiness-note').textContent),'and the note says why: '+$('exam-readiness-note').textContent);
  // The recent part is never under fifteen: with only ten good ones after the change, nothing is cut yet.
  set(step.slice(0,22)); { const c=w.mockWindowStart(step.slice(0,22)), n=w.mockRecentForm().n; ok(n>=15 && n===22-c && c<=7,'ten good mocks after the change: a cut never leaves fewer than fifteen (window '+n+')'); }
  // A change for the worse is a change too.
  const worse=[1,0,1,2,1,0,1,1,0,2,1,1, 5,4,6,4,5,4,5,6,4,5,4,5,4,5,6]; set(worse);
  ok(w.mockWindowStart(worse)===12 && w.mockRecentForm().n===15,'a change for the worse: the better mocks before it are left out as well');
  // The banner: fifteen needed, and it reads the same window.
  w.italianoComplete=()=>true; w.difficultCards=()=>[];
  const good=Array.from({length:25},(_,i)=>[1,0,1,1,0][i%5]); set(good); w.renderDashboard();
  const b=$('exam-ready-banner'), rd=w.examReady();
  ok(rd.ready && rd.n===25 && /\b25\b/.test(b.textContent) && b.classList.contains('banner-success'),'25 good mocks: ready, from all 25: '+b.textContent);
  set(good.slice(0,14)); w.renderDashboard(); ok(!w.examReady().ready && /\b15\b/.test($('exam-ready-banner').textContent),'fourteen: not yet, fifteen are still the minimum');
  // The trend chart draws each count's figure with the window as it stood then.
  set(step); const rows=w.mockTrendData();
  ok(rows.length===30 && Math.abs(rows[29].mean-(step.slice(12).reduce((a,x)=>a+x,0)/18))<1e-9 && rows[11].mean>4,'the trend rows use the window as it stood at each count');
  // The plan projects onto the same window.
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
