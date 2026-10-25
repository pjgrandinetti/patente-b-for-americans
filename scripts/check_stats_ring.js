// One readiness figure on Statistics (maintainer, 2026-10-01): the ring shows the chance of passing the next sheet (amber below 95%, green at or above), labelled so; the note beside it gives the evidence without a second percentage; no 93% average or "exam-ready" sentence anywhere; the pace comes from timed mocks when there are any. Run: node scripts/check_stats_ring.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US'; const IT=LANG.startsWith('it');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.localStorage.setItem('patente_level','3');
const sheets=(wr,time)=>wr.map((x,i)=>({date:new Date(Date.UTC(2026,9,1,18)-i*3600e3).toISOString(),correct:30-x,total:30,wrong:x,pass:x<=3,level:3,time:time?time[i]:undefined,items:[]}));
w.localStorage.setItem('patente_exam_history',JSON.stringify(sheets([2,0,1,4,1],[480,420,null,600,null])));
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const $=id=>w.document.getElementById(id);
setTimeout(()=>{
  w.document.querySelector('.nav-btn[data-screen="exam"]').click();
  const f=w.mockRecentForm(); const pct=Math.ceil((1-f.chance)*100-1e-9);
  ok($('ring-pct').textContent===w.failPctText(f.chance)+'%' && Math.abs(parseFloat($('ring-pct').textContent.replace(',','.'))-(1-f.chance)*100)<(pct<10?0.11:1.01),'the ring shows the chance of failing: '+$('ring-pct').textContent);
  // Two significant figures below 10%, rounded up; whole numbers from 10 (20261009u).
  { const it=IT, fx=x=>it?x.replace('.',','):x;
    ok(w.failPctText(1-0.0871)===fx('8.8') && w.failPctText(1-0.087)===fx('8.7') && w.failPctText(1-0.00431)===fx('0.44') && w.failPctText(1-0.1234)==='13' && w.failPctText(1-0.0996)==='10' && w.failPctText(1)==='0','two significant figures under 10%, rounded up: 8.8, 8.7, 0.44, 13, 10, 0'); }
  ok(w.document.querySelector('#readiness-ring-wrap .ring-label small').textContent===(IT?'probabilità di non superarlo':'chance of failing'),'labelled as such');
  ok($('ring-arc').classList.contains('is-short'),'amber above a 5% chance of failing');
  const note=$('exam-readiness-note').textContent;
  ok(!/%/.test(note) && /4/.test(note),'the note gives the evidence without a percentage: '+note);
  const sec=w.document.getElementById('exam-history').textContent;
  ok(!/93%|exam-ready|pronto per l/.test(sec) && !/mock avg/.test(sec),'no 93% average or exam-ready sentence');
  ok(!$('exam-form-note') || $('exam-form-note').classList.contains('hidden'),'no second chance sentence');
  const pace=$('exam-time-note').textContent;
  ok(/(timed mock exams|simulazioni cronometrate)/.test(pace) && /\b17\b/.test(pace) && /\b3\b/.test(pace),'pace from the timed mocks (480, 420, 600 s over 3 sheets): '+pace);
  // Closing rows: scores 28, 30, 29, 26, 29 and times 480, 420, 600 s (two sheets untimed).
  const foot=[...$('exam-history-table').querySelectorAll('tfoot tr')].map(r=>[...r.children].map(c=>c.textContent));
  ok(foot.length===2 && foot[0][0]===(IT?'Media':'Average') && foot[1][0]===(IT?'Deviazione standard':'Standard deviation'),'two closing rows: '+foot.map(r=>r[0]).join(' / '));
  ok(foot[0][1]===(IT?'28,4':'28.4') && foot[0][3]==='8:20','average score 28.4 and time 8:20: '+foot[0].join(' | '));
  ok(foot[1][1]===(IT?'1,5':'1.5') && foot[1][3]==='1:32','sample SD of score 1.5 and of time 1:32: '+foot[1].join(' | '));
  ok(foot.every(r=>r[2]==='' && r[4]===''),'only score and time are summarised');
  w.localStorage.setItem('patente_exam_history',JSON.stringify(sheets([0,0,0,1,0])));
  w.updateExamAvailability();
  ok(!$('ring-arc').classList.contains('is-short') && parseInt($('ring-pct').textContent)<=5,'green at 5% or less: '+$('ring-pct').textContent);
  ok(!/(timed mock exams|simulazioni cronometrate)/.test($('exam-time-note').textContent),'no timed mock: the timed-mock pace is not shown (the study pace stands in when there is one)');
  // Every mock counts, up to fifteen: seven sheets, five of them timed (the maintainer's of 2026-10-01).
  w.localStorage.setItem('patente_exam_history',JSON.stringify(sheets([3,2,0,4,2,2,0],[509,482,449,608,436,null,null])));
  w.updateExamAvailability();
  ok(w.mockRecentForm().n===7 && /7/.test($('exam-readiness-note').textContent),'seven mocks: all seven are used: '+$('exam-readiness-note').textContent);
  ok(/\b5\b/.test($('exam-time-note').textContent) && /\b17\b/.test($('exam-time-note').textContent),'the pace uses all five timed ones: '+$('exam-time-note').textContent);
  console.log('     (ring for these seven: '+$('ring-pct').textContent+')');
  w.localStorage.setItem('patente_exam_history',JSON.stringify(sheets([1,0])));
  w.updateExamAvailability();
  ok($('ring-pct').textContent==='–' && $('exam-readiness-note').textContent===w.t('fs.formOneMore'),'two sheets: no figure, and the note says one more is needed');
  const foot2=[...$('exam-history-table').querySelectorAll('tfoot tr')].map(r=>[...r.children].map(c=>c.textContent));
  ok(foot2[1][3]==='\u2013' && foot2[0][3]==='\u2013','no timed mocks: the time cells show a dash');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
