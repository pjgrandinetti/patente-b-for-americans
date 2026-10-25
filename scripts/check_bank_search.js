// The Questions tab on the Reference page (20261004y): the whole bank searched by word or phrase,
// no answers shown, and each hit opens its card even when the card is cleared. Run:
// node scripts/check_bank_search.js (UILANG=it-IT for the Italian face).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US', it=LANG.startsWith('it');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
if (process.env.STALE) html=html.replace(/<button[^>]*data-section="bank"[^>]*>[^<]*<\/button>/,'').replace(/<div id="review-pane-bank"[\s\S]*?<\/div>\s*<\/div>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}}); w.confirm=()=>true; w.alert=()=>{};
w.HTMLElement.prototype.scrollIntoView=function(){};
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const $=q=>w.document.querySelector(q), $$=q=>[...w.document.querySelectorAll(q)];
const search=q=>{const b=$('#review-search'); b.value=q; b.dispatchEvent(new w.Event('input'));};
setTimeout(()=>{
  $('[data-screen="vocab"]').click();
  const tab=$('.review-section-btn[data-section="bank"]');
  ok(tab && !tab.classList.contains('hidden'),'the Questions tab is offered');
  ok(tab && tab.textContent===(it?'Domande':'Questions'),'labelled '+(tab&&tab.textContent));
  tab.click();
  ok(!$('#review-pane-bank').classList.contains('hidden') && $('#bank-hint').textContent.length>20 && !$$('.bank-row').length,'with no query it shows only its hint');
  search('revisione del veicolo');
  let rows=$$('#review-pane-bank .bank-row');
  ok(rows.length===1 && /#24600/.test(rows[0].textContent),'the phrase finds exactly 24600');
  ok(rows[0].querySelector('.bank-hit').textContent.toLowerCase()==='revisione del veicolo','the phrase is marked where it stands');
  ok(!/\b(VERO|FALSO|True|False)\b/.test($('#review-pane-bank').textContent),'no answer is shown');
  ok(it ? !rows[0].querySelector('.bank-en') : !!rows[0].querySelector('.bank-en'),it?'no English for an Italian browser':'the English translation is shown');
  ok(tab.dataset.count==='1','the tab carries the count');
  search('revision');
  ok($$('#review-pane-bank .bank-row').length>=10,'a word prefix reaches the inflected forms: '+$$('#review-pane-bank .bank-row').length);
  search('veicolo');
  const n=Number(tab.dataset.count);
  ok(n>1000 && $$('#review-pane-bank .bank-row').length===50 && /50/.test($('.bank-more').textContent),'a common word is capped at 50 of '+n);
  ok(/veicol[aeio]/i.test($$('.bank-hit').map(m=>m.textContent).join(' ')) && $$('.bank-hit').some(m=>/veicoli/i.test(m.textContent)),'veicolo also finds veicoli');
  search('l’inversione di marcia');
  ok(Number(tab.dataset.count)>0,'a typographic apostrophe matches the plain one: '+tab.dataset.count);
  // clear card 4617 at the current level, then open it from the search
  const prog=w.eval('progress'); const q=w.eval('questions').find(c=>c.id===4617);
  prog[4617]=prog[4617]||{st:{}}; prog[4617].st=prog[4617].st||{};
  q.statements.forEach(st=>{prog[4617].st[st.number]={seen:2,correct:2,streak:2,given:st.answer,gAt:1,sAt:1};});
  ok(w.cardCleared(4617),'card 4617 is cleared');
  ok(!w.buildQueue('topic',q.topic).includes(4617),'so the study queue no longer holds it');
  search('revisione del veicolo');
  $('#review-pane-bank .bank-open').click();
  ok($('#screen-study').classList.contains('active'),'Open card goes to the study screen');
  ok(w.eval('currentQuestion()').id===4617,'on card 4617');
  ok(!!$('#card-statements .statement-item[data-number="24600"]'),'showing the statement found');
  ok(w.eval('cardWorkTarget()').el.dataset.number==='24600','and aimed at it');
  $('#btn-next').click();
  ok($('#screen-vocab').classList.contains('active'),'finishing the card returns to Reference');
  ok($('#review-search').value==='revisione del veicolo' && $$('#review-pane-bank .bank-row').length===1,'with the search intact');
  // At Solo italiano the English is neither shown nor searched (maintainer, 2026-09-29).
  w.eval('currentLevel = EXAM_LEVEL');
  search('revisione del veicolo');
  ok($$('#review-pane-bank .bank-row').length===1 && !$('#review-pane-bank .bank-en'),'at Italian only the hit shows no English');
  search('inspection');
  ok(!$$('#review-pane-bank .bank-row').length,'and an English word finds nothing there');
  // A question number, and adding a question to the weak spots from here (20261011r).
  search('19522');
  { const rows=$$('#review-pane-bank .bank-row');
    ok(rows.length===1 && /#19522/.test(rows[0].textContent),'a question number finds that question');
    search('#19522'); ok($$('#review-pane-bank .bank-row').length===1,'with a # too');
    const pin=$('#review-pane-bank .bank-pin'); ok(pin && /(Add to weak spots|Aggiungi ai punti deboli)/.test(pin.textContent),'each row offers to add it to the weak spots');
    pin.click();
    ok(w.weakPinned(4105,'19522') && pin.classList.contains('is-on') && /(In your weak spots|Nei punti deboli)/.test(pin.textContent),'a tap adds it, and the button says so');
    ok(w.difficultCards().some(d=>d.id===4105 && d.stmts.includes('19522')),'it is now among the weak spots');
    pin.click(); ok(!w.weakPinned(4105,'19522'),'a second tap takes it back'); }
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
