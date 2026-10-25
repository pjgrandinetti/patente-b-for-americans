// The Grammar tab on the Reference page: English prose with every example a
// live VERO statement quoted from the bank by number, marked at the run of
// words the section is about; searched on its phrases; absent for an Italian browser;
// built by ensureGrammarPane on an index.html that lacks it.
// Run: node scripts/check_grammar_tab.js (UILANG=it-IT; STALE=1; SRC=; JSDOM=).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US';
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
if(process.env.STALE){ // a cached page from before the tab existed
  html=html.replace(/<button class="review-section-btn hidden" data-section="grammar"[^>]*>Grammar<\/button>\s*/,'')
           .replace(/<!-- Grammar[\s\S]*?<div id="grammar-body"><\/div>\s*<\/div>\s*/,'');
  if(/review-pane-grammar|data-section="grammar"/.test(html)) throw new Error('STALE strip failed');
}
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
const spoken=[]; w.speechSynthesis={getVoices:()=>[],cancel(){},speak(u){spoken.push(u.text)}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{constructor(t){super();this.text=t}};
const gr=JSON.parse(fs.readFileSync(root+'/grammar.json','utf8'));
const qs=JSON.parse(fs.readFileSync(root+'/questions.json','utf8'));
const byNum={}; for(const q of qs)for(const s of q.statements)byNum[String(s.number)]=s;
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  w.document.querySelector('[data-screen="vocab"]')?.click();
  const tab=w.document.querySelector('.review-section-btn[data-section="grammar"]');
  if(LANG.startsWith('it')){
    ok(tab && tab.classList.contains('hidden'),'an Italian browser has no Grammar tab');
    ok(!w.eval('reviewSectionsAvailable')().includes('grammar'),'and the section is not available');
    console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
  }
  ok(tab && !tab.classList.contains('hidden'),'the Grammar tab is offered'+(process.env.STALE?' (built on a stale page)':''));
  ok(w.eval('reviewSectionsAvailable')().indexOf('grammar')===1,'right after Vocabulary');
  tab.click();
  const pane=w.document.getElementById('review-pane-grammar');
  ok(pane && !pane.classList.contains('hidden'),'tapping it shows the pane');
  ok(w.document.getElementById('review-pane-vocab').classList.contains('hidden'),'and hides Vocabulary');
  const topics=[...pane.querySelectorAll('details.gr-topic')];
  ok(topics.length===gr.topics.length,'one disclosure per topic: '+topics.length);
  ok(gr.topics.length===1 ? topics[0].open : topics.every(d=>!d.open),'a single topic opens unfolded; several open folded');
  const expand=pane.querySelector('[data-gr-fold="open"]'), collapse=pane.querySelector('[data-gr-fold="close"]');
  ok(expand && collapse,'Expand all and Collapse all buttons are drawn');
  expand.click();
  ok(topics.every(d=>d.open),'Expand all opens every topic');
  collapse.click();
  ok(topics.every(d=>!d.open),'Collapse all closes every topic');
  expand.click();
  const nSec=gr.topics.reduce((a,t)=>a+t.sections.length,0), nEx=gr.topics.reduce((a,t)=>a+t.sections.reduce((b,s)=>b+(s.ex||[]).length,0),0);
  ok(pane.querySelectorAll('.gr-sec:not(.gr-recap-sec)').length===nSec,'every section rendered: '+nSec);
  const exs=[...pane.querySelectorAll('.gr-ex')];
  ok(exs.length===nEx,'every example rendered: '+nEx);
  const flat=gr.topics.flatMap(t=>t.sections.flatMap(s=>s.ex||[]));
  let textOk=true, markOk=true, enOk=true;
  exs.forEach((el,i)=>{
    const st=byNum[String(flat[i].n)];
    if(!el.querySelector('.gr-it').textContent.includes(st.italian_text)) textOk=false;
    const m=el.querySelector('mark.gr-hit'); if(!m || m.textContent.toLowerCase()!==flat[i].hl.toLowerCase()) markOk=false;
    if(el.querySelector('.gr-en').textContent!==st.english_translation) enOk=false;
  });
  ok(textOk,'each example prints the statement exactly as the bank has it');
  ok(markOk,'and marks exactly the run of words named');
  ok(enOk,'with the bank\'s own English underneath');
  ok(!/VERO|FALSO/.test(pane.textContent),'no answer printed anywhere');
  exs[0].querySelector('.gr-speak').click();
  ok(spoken.length===1 && spoken[0].includes(byNum[String(flat[0].n)].italian_text),'🔊 reads the Italian');
  // the teaching shape: English concept lines in the intro, an `after`
  // pointer under each example group, and a recap table last
  ok(pane.querySelectorAll('.gr-intro .gr-enx').length>=3,'the intro shows the concept on English sentences');
  const secs=[...pane.querySelectorAll('.gr-sec:not(.gr-recap-sec)')];
  ok(secs.every(sc=>sc.querySelectorAll('.gr-ex').length>=1 && sc.querySelectorAll('.gr-ex').length<=2),'every point carries one or two examples, right after it');
  ok(secs.every(sc=>sc.querySelector('.gr-after')),'and closes by pointing at the form in the example');
  ok(topics.every(d=>d.querySelector('.gr-recap-sec') && d.lastElementChild.classList.contains('gr-recap-sec')),'the recap table is LAST in every topic');
  // Hide the English: the examples become a self-test
  const tog=pane.querySelector('[data-gr-en]'); ok(!!tog,'a Hide the English control');
  tog.click();
  const pane2=w.document.getElementById('review-pane-grammar');
  ok(pane2.classList.contains('gr-en-hidden') && pane2.querySelector('[data-gr-en]').textContent==='Show the English','hiding is remembered and the control flips');
  const ex0=pane2.querySelector('.gr-ex'); ex0.click();
  ok(ex0.classList.contains('gr-reveal'),'a tap on an example reveals its own English');
  pane2.querySelector('[data-gr-en]').click();
  ok(!w.document.getElementById('review-pane-grammar').classList.contains('gr-en-hidden'),'and Show the English puts them all back');
  // a search REACHES the Grammar tab (20261002x): the points that teach the
  // phrase typed, matched on the phrases they name, never on the prose
  const box=w.document.getElementById('review-search');
  const search=q=>{box.value=q; box.dispatchEvent(new w.Event('input',{bubbles:true}));};
  search('sorpassati');
  ok(!pane.classList.contains('hidden') && Number(tab.dataset.count)>0,'a search for `sorpassati` shows the Grammar pane with a count: '+tab.dataset.count);
  ok(pane.querySelector('details.gr-topic[open][data-gr="who"]'),'and the topic that teaches it is open');
  ok(!pane.querySelector('.gr-tools') && !pane.querySelector('.gr-intro'),'with no tools row and no intro, only the points');
  const secH=[...pane.querySelectorAll('.gr-sec h4')].map(h=>h.textContent);
  ok(secH.some(h=>/si viene sorpassati/.test(h)),'the point naming the phrase is among them: '+secH.join(' | '));
  search('viene sorpassato');
  ok(Number(tab.dataset.count)>0 && pane.querySelector('mark.gr-hit'),'a two-word phrase reaches the example that marks it');
  search('chiuso');
  ok(!Number(tab.dataset.count||0),'a word only in the prose and the intro (`chiuso`) reaches nothing: neither is searched');
  search('vietata');
  ok(Number(tab.dataset.count)>0,'`vietata` reaches the ban topic');
  tab.click();
  ok(box.value==='vietata' && !pane.classList.contains('hidden'),'tapping Grammar during a search narrows to it and keeps the query');
  w.document.querySelector('.review-section-btn[data-section="weak"]').click();
  ok(box.value==='','Ambiguous still parks the query');
  w.document.querySelector('.review-section-btn[data-section="vocab"]').click();
  ok(box.value==='vietata','and the next list tapped gets it back');
  search(''); tab.click();
  ok(pane.querySelector('.gr-tools') && pane.querySelector('.gr-intro'),'clearing the box restores the full tab');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
