// After the theory exam is passed (20261030g, maintainer, 2026-10-30): nothing asks for theory work (no Begin/Resume, no
// weak-spots, mock or exam-date Settings groups), the theory stays as reference with the key points linked from the
// box, nothing is deleted, and the box celebrates: the learner's own journey and a one-time confetti burst.
// Run: node scripts/check_after_pass.js (UILANG=it-IT; SRC= another public_html).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US', IT=LANG.startsWith('it');
const key=n=>{const d=new Date(); d.setDate(d.getDate()+n); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');};
const bank=JSON.parse(fs.readFileSync(root+'/questions.json','utf8')).filter(q=>q.statements.some(s=>!s.retired));
// Three statements answered right at Italiano, the first of them 100 days before the exam (yesterday).
const start=new Date(); start.setHours(12,0,0,0); start.setDate(start.getDate()-101);
const L3={}; bank.slice(0,3).forEach((q,i)=>{const s=q.statements.find(x=>!x.retired); L3[q.id]={lastSeen:start.toISOString(),st:{[s.number]:{seen:1,correct:1,streak:1,given:s.answer,gAt:start.getTime()+i*864e5}}};});
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.localStorage.setItem('patente_level','3');
w.localStorage.setItem('patente_progress_L3',JSON.stringify(L3));
const good=[1,0,1,1,0,2,1,0,1,1,0,1,1,0,1];
w.localStorage.setItem('patente_exam_history',JSON.stringify(good.map((x,i)=>{const d=new Date(); d.setDate(d.getDate()-2-i); return {date:d.toISOString(),correct:30-x,total:30,wrong:x,pass:true,level:3,items:[]};})));
w.localStorage.setItem('patente_exam_date',key(-1));
let reduced=false;
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollTo=function(){}; w.Element.prototype.scrollIntoView=function(){}; w.alert=()=>{};
w.matchMedia=q=>({matches: /reduced-motion/.test(q) ? reduced : false, addEventListener(){}, addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const $=id=>w.document.getElementById(id);
const vis=el=>!!el&&!el.closest('.hidden');
setTimeout(()=>{
  w.italianoComplete=()=>true; w.renderDashboard(); w.updateResumeButton(); w.ensureSettingsGroups(); w.updateSettingsGroups();
  ok(!$('sg-after').classList.contains('hidden'),'before the answer the weak spots and mocks group shows');
  $('exam-date-box').querySelector('[data-ed=pass]').click();
  w.updateResumeButton(); w.updateSettingsGroups();
  const box=$('exam-date-box'), txt=box.textContent;
  ok(/(🎉 Congratulations, you passed the theory exam!|🎉 Complimenti, hai superato l’esame di teoria!)/.test(txt),'the box opens with a celebration');
  ok(/(for about 3 months, and you’ve finally made it! You’re not done yet, but this was a big accomplishment\. Again, congratulations on obtaining your foglio rosa\.|da circa 3 mesi, e finalmente ce l’hai fatta! Non hai ancora finito, ma è stato un grande traguardo\. Ancora complimenti per il tuo foglio rosa\.)/.test(txt) && !/(mock exams|simulazioni)\b.*\d/.test((box.querySelector('.exam-date-journey')||{}).textContent||''),'the journey in the maintainer\'s words, 100 days reading about 3 months, with no counts (20261030h): '+(box.querySelector('.exam-date-journey')||{}).textContent);
  ok(!!box.querySelector('[data-ed=keypoints]') && /(foglio rosa)/.test(txt),'the key points stay one tap away, beside the foglio rosa facts');
  ok(w.document.querySelectorAll('.confetti-layer .confetti').length>50,'confetti the first time');
  w.document.querySelectorAll('.confetti-layer').forEach(e=>e.remove()); w.renderDashboard();
  ok(!w.document.querySelector('.confetti-layer'),'and only the first time on this device');
  ok(!vis($('nav-resume')),'no Begin or Resume after a pass');
  ok($('sg-after').classList.contains('hidden') && $('sg-review').classList.contains('hidden'),'no weak-spots, mock or exam-date Settings groups after a pass');
  ok(!vis($('dash-next')) && !vis($('exam-ready-banner')),'no weak-spots or mock card and no readiness banner');
  ok(Object.keys(JSON.parse(w.localStorage.getItem('patente_progress_L3'))).length===3 && JSON.parse(w.localStorage.getItem('patente_exam_history')).length===15,'nothing is deleted');
  // Change my answer, then a pass again with reduced motion: no confetti.
  box.querySelector('[data-ed=undo]').click(); w.localStorage.removeItem('patente_pass_celebrated'); reduced=true;
  $('exam-date-box').querySelector('[data-ed=pass]').click();
  ok(!w.document.querySelector('.confetti-layer'),'no confetti when reduced motion is asked for');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
