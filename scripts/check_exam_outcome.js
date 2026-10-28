// The exam day and after the exam (20261029l, maintainer, 2026-10-29). On the day the review and the mock exam stay;
// once the date has passed the box asks how it went, then says what comes next for a pass or a fail.
// Run: node scripts/check_exam_outcome.js (UILANG=it-IT; SRC= another public_html).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US', IT=LANG.startsWith('it');
const key=n=>{const d=new Date(); d.setDate(d.getDate()+n); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.localStorage.setItem('patente_level','3');
const good=[1,0,1,1,0,2,1,0,1,1,0,1,1,0,1];
w.localStorage.setItem('patente_exam_history',JSON.stringify(good.map((x,i)=>{const d=new Date(); d.setDate(d.getDate()-2-i); return {date:d.toISOString(),correct:30-x,total:30,wrong:x,pass:true,level:3,items:[]};})));
w.localStorage.setItem('patente_exam_date',key(0));
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollTo=function(){}; w.Element.prototype.scrollIntoView=function(){}; w.alert=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const $=id=>w.document.getElementById(id);
const box=()=>$('exam-date-box');
const vis=el=>el&&!el.classList.contains('hidden');
const click=act=>box().querySelector(`[data-ed=${act}]`).click();
setTimeout(()=>{
  w.italianoComplete=()=>true; w.renderDashboard();
  // the exam day
  let txt=box().textContent;
  ok(/(Your exam is today|Il tuo esame è oggi)/.test(txt),'the exam day reads as today');
  ok(/(later in the day|più tardi nella giornata)/.test(txt) && /(20 minutes for 30|20 minuti per 30)/.test(txt),'its advice keeps the review and mock for a late exam, and gives the room\'s time');
  ok(!!box().querySelector('[data-row=review]') && !!box().querySelector('[data-row=mock]'),'the review and mock rows stay on the exam day');
  ok(!box().querySelector('[data-row=waiting]'),'no Still waiting row on the exam day');
  ok(vis($('dash-next')),'the mock card stays on the exam day');
  ok(!box().querySelector('[data-ed=pass]'),'nothing asks how it went on the day itself');
  // the day after
  w.localStorage.setItem('patente_exam_date',key(-1)); w.renderDashboard();
  txt=box().textContent;
  ok(/(How did your theory exam|Com’è andato l’esame)/.test(txt) && box().querySelector('[data-ed=pass]') && box().querySelector('[data-ed=fail]') && box().querySelector('[data-ed=postponed]'),'the day after, the box asks how it went: '+txt.slice(0,60));
  ok(!vis($('exam-ready-banner')),'the readiness banner goes while it asks');
  // a pass
  click('pass');
  ok(JSON.parse(w.localStorage.getItem('patente_exam_outcome')).length===1 && !w.localStorage.getItem('patente_exam_date'),'a pass is recorded and the date cleared');
  txt=box().textContent;
  ok(/(Congratulations|Complimenti)/.test(txt) && /(foglio rosa)/.test(txt) && /(12 months|12 mesi)/.test(txt),'a pass says what comes next: '+txt.slice(0,80));
  ok(vis(box()) && !vis($('exam-ready-banner')) && !vis($('dash-next')),'after a pass no banner and no mock or weak-spots card');
  ok('examOutcome' in w.buildProgressBundle().settings,'the outcome travels with the synced settings');
  click('undo');
  ok(!!box().querySelector('[data-ed=pass]') && !w.localStorage.getItem('patente_exam_outcome'),'Change my answer asks again');
  // a fail
  click('fail');
  txt=box().textContent;
  const [y,m,d]=key(-1).split('-').map(Number); const again=new Date(y,m,d);
  const againWords=new Intl.DateTimeFormat(IT?'it-IT':'en-US',{weekday:'long',month:'long',day:'numeric'}).format(again);
  ok(txt.includes(againWords),'a fail gives the first day it may be taken again, a month on: '+againWords);
  ok(/(6 months|6 mesi)/.test(txt) && !!box().querySelector('[data-ed=bank]') && !!box().querySelector('#exam-date-input'),'it names the six months, opens the Questions tab, and asks for the new date');
  ok(!vis($('exam-ready-banner')),'no readiness banner after a fail until a new date');
  box().querySelector('#exam-date-input').value=key(40); click('set');
  ok(/(Your exam is in 40 days|tra 40 giorni)/.test(box().textContent),'a new date brings back the countdown');
  // a second fail
  w.localStorage.setItem('patente_exam_date',key(-2)); w.renderDashboard(); click('fail');
  ok(/(new application|nuova domanda)/.test(box().textContent),'a second fail says a new application is needed');
  // postponed
  w.localStorage.removeItem('patente_exam_outcome'); w.localStorage.setItem('patente_exam_date',key(-1)); w.renderDashboard(); click('postponed');
  ok(!w.localStorage.getItem('patente_exam_outcome') && !!box().querySelector('#exam-date-input') && !box().querySelector('[data-ed=bank]'),'postponed records nothing and asks for the date');
  // the Questions tab link
  w.localStorage.setItem('patente_exam_outcome',JSON.stringify([{d:key(-3),r:'fail'}])); w.localStorage.removeItem('patente_exam_date'); w.renderDashboard();
  click('bank');
  ok(!$('screen-vocab').classList.contains('hidden') && w.eval('reviewSection')==='bank','the link opens the Questions tab');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
