// The mock sheet behaves like the Ministry's terminal: any order, editable
// answers, a Riepilogo before closing, no feedback until then, unanswered
// counted as wrong. Run: node scripts/check_exam_sheet.js  (UILANG=it-IT for
// the Italian face; SRC= a public_html directory to test another build;
// JSDOM= the path to a jsdom install, default /tmp/node_modules/jsdom).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:process.env.UILANG||'en-US'});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}}); w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}};
let confirms=[]; w.confirm=(m)=>{confirms.push(m); return true;};
w.localStorage.setItem('patente_level','3');
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const $=id=>w.document.getElementById(id);
setTimeout(()=>{
  try{ w.eval("setLevel(3)"); }catch{}
  w.document.querySelector('[data-screen="exam"]')?.click();
  w.eval('startExam()');
  const st=()=>w.eval('examState');
  ok(!!$('exam-sheet') && !$('exam-in-progress').classList.contains('hidden'),'the sheet is built and shown');
  ok(st().answers.length===30 && st().answers.every(a=>a===null),'thirty empty slots');
  ok(w.document.querySelectorAll('.exam-chip').length===10 && w.document.querySelectorAll('.exam-group').length===3,'ten chips shown under three group tabs');
  const vf=c=>w.document.querySelector(`.exam-vf-btn[data-choice="${c}"]`);
  vf('VERO').click();
  ok(st().index===0,'answering does not advance');
  ok(vf('VERO').getAttribute('aria-pressed')==='true' && vf('FALSO').getAttribute('aria-pressed')==='false','the choice is marked on the pair');
  ok(!w.document.querySelector('#exam-sheet .right, #exam-sheet .wrong, #exam-sheet .correct'),'no feedback on the sheet');
  vf('FALSO').click();
  ok(st().answers[0].chosen==='FALSO','an answer can be changed');
  ok(w.document.querySelector('.exam-chip[data-index="0"]').classList.contains('done'),'the chip shows an answer on record');
  $('exam-next').click();
  ok(st().index===1 && $('exam-counter').textContent.includes('2'),'Successiva moves to the second statement');
  ok(vf('VERO').getAttribute('aria-pressed')==='false' && vf('FALSO').getAttribute('aria-pressed')==='false','the pair is blank on an unanswered statement');
  $('exam-prev').click();
  ok(st().index===0 && vf('FALSO').getAttribute('aria-pressed')==='true','Precedente returns and the answer is still there');
  ok($('exam-prev').disabled,'Precedente is disabled on the first');
  ok(!w.document.querySelector('.exam-chip[data-index="17"]'),'chip 18 is not shown while group 1-10 is open');
  w.document.querySelector('.exam-group[data-group="1"]').click();
  ok(st().index===0 && !!w.document.querySelector('.exam-chip[data-index="17"]'),'a group tab opens 11-20 without leaving the statement');
  w.document.querySelector('.exam-chip[data-index="17"]').click();
  ok(st().index===17 && w.document.querySelector('.exam-group.open').dataset.group==='1','a chip jumps to its statement');
  w.eval('goExamStatement(25)');
  ok(w.document.querySelector('.exam-group.open').dataset.group==='2' && !!w.document.querySelector('.exam-chip.current[data-index="25"]'),'moving to a statement opens its group and underlines it');
  // answer every statement correctly except two, leave one blank
  const items=st().items;
  for(let i=0;i<30;i++){ if(i===29) continue; w.eval(`goExamStatement(${i})`); const right=items[i].stmt.answer; const pick=(i===3||i===7)?(right==='VERO'?'FALSO':'VERO'):right; vf(pick).click(); }
  w.eval('goExamStatement(29)');
  ok($('exam-next').textContent.includes(w.eval("xt('exam.next')")) && $('exam-next').disabled,'on the last statement Successiva is inactive, as on the terminal');
  $('exam-next').click();
  ok(st().index===29 && $('exam-summary').classList.contains('hidden'),'and pressing it does nothing');
  $('exam-summary-btn').click();
  ok(/^\d+:\d\d$/.test($('exam-timer-summary').textContent) && $('exam-close').textContent===w.eval("xt('exam.close')") && /^Termina esame$/.test($('exam-close').textContent),'the Riepilogo shows the clock and ends with Termina esame');
  ok(!$('exam-summary').classList.contains('hidden') && $('exam-sheet').classList.contains('hidden'),'the Riepilogo replaces the sheet');
  ok(w.document.querySelectorAll('.exam-summary-row').length===30,'thirty rows in the Riepilogo');
  // As the terminal draws it (20261008v): Italian labels in every browser, a row per question with its figure and the V and F squares, the chosen one crossed, and a flag.
  ok($('exam-summary-title').textContent==='Riepilogo risposte' && $('exam-summary-back').textContent==='Indietro' && $('exam-close').textContent==='Termina esame','the Riepilogo is labelled in Italian whatever the browser');
  const r0=w.document.querySelector('.exam-summary-row[data-index="0"]'), withFig=st().items.findIndex(it=>it.q.image);
  ok(r0.querySelectorAll('.exam-sum-vf').length===2 && r0.querySelectorAll('.exam-sum-vf.chosen').length===1 && r0.querySelector('.exam-sum-vf.chosen').textContent===(st().answers[0].chosen==='VERO'?'V':'F'),'each row shows V and F with the chosen one crossed');
  ok(withFig<0 || !!w.document.querySelector(`.exam-summary-row[data-index="${withFig}"] .exam-summary-fig img`),'a question with a figure shows it in its row');
  ok(w.document.querySelectorAll('.exam-summary-row[data-index="29"] .exam-sum-vf.chosen').length===0,'the unanswered row has neither crossed');
  const fl=w.document.querySelector('.exam-summary-row[data-index="2"] .exam-sum-flag'); fl.click();
  ok(st().marks[2]===true && fl.classList.contains('is-on') && !$('exam-summary').classList.contains('hidden'),'a tap on a row\'s flag marks the question and stays on the Riepilogo');
  ok($('exam-summary-note').textContent.startsWith('1 '),'the note counts one unanswered: '+$('exam-summary-note').textContent);
  ok(w.document.querySelectorAll('.exam-summary-row.blank').length===1,'the blank row is marked');
  w.document.querySelector('.exam-summary-row[data-index="5"]').click();
  ok(st().index===5 && !$('exam-sheet').classList.contains('hidden'),'a Riepilogo row returns to its statement');
  ok($('exam-counter').textContent==='Domanda 6 di 30' && $('exam-answer-label').textContent==='Risposta' && $('exam-prev').textContent.includes('Precedente'),'the sheet is labelled in Italian whatever the browser');
  w.eval('goExamStatement(2)'); ok($('exam-mark').classList.contains('is-on'),'the marked question shows its bookmark filled');
  $('exam-mark').click(); ok(st().marks[2]===false && !$('exam-mark').classList.contains('is-on'),'the bookmark unmarks it');
  ok(w.document.querySelectorAll('.exam-chip .exam-tick').length===10 && w.document.querySelector('.exam-group[data-group="0"] .exam-tick2') && !w.document.querySelector('.exam-group[data-group="2"] .exam-tick2'),'answered chips carry a tick; a group with all ten answered carries a double tick, the one with a blank does not');
  w.eval('goExamStatement(5)');
  $('exam-summary-btn').click();
  ok(!$('exam-summary').classList.contains('hidden'),'the Riepilogo button reopens it');
  ok(st().timerHandle!=null && /^\d\d:\d\d$/.test($('exam-timer-sheet').textContent),'the timer runs in the sheet\'s own clock box until the sheet is closed');
  $('exam-close').click();
  ok(confirms.length===1 && /^1 senza risposta/.test(confirms[0]) && /Confermi di voler concludere l’esame in corso\?/.test(confirms[0]) && !/unanswered|end the exam|\n/.test(confirms[0]),'ending asks once, in Italian only, naming the blank: '+confirms[0]);
  const hist=JSON.parse(w.localStorage.getItem('patente_exam_history'));
  const r=hist[0];
  ok(r.total===30 && r.correct===27 && r.wrong===3,'stored 27 of 30, 3 wrong (two misses plus the blank): '+JSON.stringify([r.total,r.correct,r.wrong]));
  { const d=$('exam-score-display').textContent; ok(/Esatte\s*27/.test(d) && /Errate\s*3/.test(d) && /Esito esame\s*Idoneo/.test(d) && $('exam-result-msg').textContent==='' && !/[Pp]assed|Correct|Wrong/.test(d),'the result reads as the terminal\'s: '+d.replace(/\s+/g,' ')); }
  ok(r.pass===true,'three wrong still passes');
  ok(r.items.filter(x=>x.chosen==null).length===1,'the blank is stored as unanswered');
  ok(!$('exam-results').classList.contains('hidden') && $('exam-in-progress').classList.contains('hidden'),'the score shows and the sheet hides');
  ok(w.eval('sheetWrong')(r)===3,'sheetWrong agrees with the stored count');
  // a second sheet starts clean
  w.eval('startExam()');
  ok(st().answers.every(a=>a===null) && st().index===0 && $('exam-summary').classList.contains('hidden') && !$('exam-sheet').classList.contains('hidden'),'a second sheet starts empty at the first statement');
  ok(w.document.querySelectorAll('#exam-sheet').length===1,'the sheet is built once');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
