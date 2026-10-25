// The exam date (maintainer, 2026-10-03): once the learner is at the bar the dashboard asks for the official exam's date, counts the days down and paces the mock exams, one a day at least; the date is a synced setting, and a past date is dropped. Run: node scripts/check_exam_date.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US', IT=LANG.startsWith('it');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const sheets=(wr,daysAgo=1)=>wr.map((x,i)=>{const d=new Date(); d.setDate(d.getDate()-daysAgo-i); d.setHours(12,0,0,0); return {date:d.toISOString(),correct:30-x,total:30,wrong:x,pass:x<=3,level:3,items:[]};});
const key=n=>{const d=new Date(); d.setDate(d.getDate()+n); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
setTimeout(()=>{
  const $=id=>w.document.getElementById(id); const box=()=>$('exam-date-box');
  const good=[1,0,1,1,0,2,1,0,1,1,0,1,1,0,1];
  const draw=h=>{ w.localStorage.setItem('patente_exam_history',JSON.stringify(h)); w.italianoComplete=()=>true; w.difficultCards=()=>[]; w.renderDashboard(); };
  draw(sheets(Array(15).fill(2)));
  ok(!box() || box().classList.contains('hidden'),'not at the bar, no date: nothing is asked');
  draw(sheets(good));
  ok(box() && !box().classList.contains('hidden') && box().nextElementSibling===$('dash-next') && box().querySelector('input[type=date]') && /(When is your exam\?|Quando è il tuo esame\?)/.test(box().textContent),'at the bar: the date is asked for, right above the mock exam card');
  box().querySelector('input').value=key(-2); box().querySelector('[data-ed=set]').click();
  ok(w.examDate()===null && box().querySelector('input'),'a past date is refused');
  const t0=Number(w.localStorage.getItem('patente_settings_ts')||0);
  box().querySelector('input').value=key(9); box().querySelector('[data-ed=set]').click();
  ok(w.examDate()===key(9) && !box().querySelector('input') && /(in 9 days|tra 9 giorni)/.test(box().textContent),'set nine days out: the countdown reads nine days: '+box().textContent);
  ok($('exam-ready-banner').classList.contains('hidden'),'with a date entered the ready banner goes');
  ok(/(then one mock exam\. Time left over is best spent continuing the review|poi una simulazione\. Il tempo che avanza \u00e8 meglio spenderlo continuando il ripasso)/.test(box().textContent) && /^(not taken yet|non ancora svolta)$/.test(box().querySelector('[data-row=mock] dd').textContent),'the pace is the review, then one mock a day, spare time to the review (20261023f); the mock row reads not taken yet');
  w.setExamDate(key(7)); draw(sheets(good));
  ok(/(With the exam this close, do as much of the review as you can|Con l\u2019esame cos\u00ec vicino, fai quanto pi\u00f9 ripasso riesci)/.test(box().textContent) && !/(hour a day|ora al giorno)/.test(box().textContent),'seven days out the hour goes and the box asks for as much review as possible, in sittings (20261023g)');
  w.setExamDate(key(8)); draw(sheets(good));
  ok(/(hour a day|ora al giorno)/.test(box().textContent),'eight days out the hour a day stands');
  w.setExamDate(key(9)); draw(sheets(good));
  ok(/^(none left|nessuna)$/.test(box().querySelector('[data-row=review] dd').textContent) && !box().querySelector('[data-row=waiting]') && !box().querySelector('[data-ed=review]'),'with nothing to review the box says so and offers no button');
  ok(w.buildProgressBundle().settings.examDate===key(9),'the date rides in the synced settings');
  draw(sheets([1],0).concat(sheets(good)));
  ok(/^(done|svolta)$/.test(box().querySelector('[data-row=mock] dd').textContent),'a mock taken today: the row reads done');
  { const card=$('dash-mock'), btn=$('btn-dash-mock');
    ok(card && /(Today’s mock exam: done|Simulazione di oggi: fatta)/.test(card.textContent) && btn.classList.contains('btn-secondary') && /(Take another|Fanne un’altra)/.test(btn.textContent),'the mock card says today\'s is done, with a quieter button to take another (20261011i)'); }
  { const d=new Date(); const six=Array.from({length:6},(_,i)=>({date:new Date(d.getTime()-i*60e3).toISOString(),correct:29,total:30,wrong:1,pass:true,level:3,items:[]}));
    draw(six.concat(sheets(good))); ok(/^(6 taken|6 svolte)$/.test(box().querySelector('[data-row=mock] dd').textContent) && !/(is enough|basta)/.test(box().textContent),'six today: the count, and no line saying one is enough (20261021c)'); }
  draw(sheets(Array(15).fill(2)));
  ok(!box().classList.contains('hidden') && /(9 days|9 giorni)/.test(box().textContent),'a date once set stays on screen when the mocks slip below the bar');
  ok(!$('exam-ready-banner').classList.contains('hidden') && $('exam-ready-banner').classList.contains('banner-warn'),'and the warning banner still shows above it');
  w.localStorage.setItem('patente_exam_date',key(1)); draw(sheets(good)); ok(/(tomorrow|domani)/.test(box().textContent),'one day out: tomorrow');
  w.localStorage.setItem('patente_exam_date',key(0)); draw(sheets(good)); ok(/(is today|è oggi)/.test(box().textContent) && !/(a day|al giorno)/.test(box().textContent),'the day itself: today, no pacing');
  w.localStorage.setItem('patente_exam_date',key(-1)); draw(sheets(good)); ok(w.examDate()===null && box().querySelector('input'),'a date that has passed is dropped and asked for again');
  w.localStorage.setItem('patente_exam_date',key(5)); draw(sheets(good)); box().querySelector('[data-ed=change]').click();
  ok(box().querySelector('input').value===key(5) && box().querySelector('[data-ed=remove]'),'Change reopens the field with the date, and offers Remove');
  box().querySelector('[data-ed=remove]').click(); ok(!$('exam-ready-banner').classList.contains('hidden'),'and comes back when the date is removed'); ok(w.examDate()===null && w.buildProgressBundle().settings.examDate===null,'Remove clears it');
  // a merge from another device
  w.localStorage.setItem('patente_settings_ts','1'); w.mergeSyncSettings({t:Date.now()+5000,examDate:key(12)}); ok(w.examDate()===key(12),'a newer bundle\'s date is taken');
  w.localStorage.setItem('patente_settings_ts','1'); w.mergeSyncSettings({t:Date.now()+9000}); ok(w.examDate()===key(12),'a bundle that does not know the key leaves it alone');
  ok(IT ? !/exam|Set\b/.test(box().textContent) : true,'in the reader\'s language');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
