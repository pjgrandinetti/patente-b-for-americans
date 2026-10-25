// The licensing How-to in two route tabs (maintainer, 2026-10-01): a driving school (default) and a private candidate, each eight numbered steps with its own Cost paragraph; the choice is remembered and survives a repaint; the projection's "ready" link opens the theory-exam step of the tab showing. Run: node scripts/check_howto_tabs.js (UILANG=it-IT; STALE=1 is not needed, the panel is repainted from STATIC_IT for Italian).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US'; const IT=LANG.startsWith('it');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
let scrolled=null; w.Element.prototype.scrollIntoView=function(){ scrolled=this; };
w.requestAnimationFrame=cb=>setTimeout(cb,0);
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  const box=w.document.querySelector('[data-i18n-html="next.body"]');
  const tabs=()=>[...box.querySelectorAll('.route-tab')], panes=()=>[...box.querySelectorAll('.route-pane')];
  const shown=()=>panes().filter(p=>!p.classList.contains('hidden')).map(p=>p.dataset.route);
  ok(tabs().length===2 && panes().length===2,'two tabs and two panes');
  ok(tabs()[0].textContent===(IT?'Con un’autoscuola':'Through a driving school') && tabs()[1].textContent===(IT?'Da privatista':'As a private candidate'),'tab names: '+tabs().map(t=>t.textContent).join(' | '));
  ok(shown().join()==='school' && tabs()[0].classList.contains('is-on'),'the school route shows by default');
  ok(panes().every(p=>p.querySelectorAll('ol > li').length===9 && p.querySelectorAll('li.step-theory').length===1),'each route has nine steps and one theory-exam step');
  ok(panes().every(p=>/(Cost|Costi)\./.test(p.querySelector(':scope > p')?.textContent||'')),'each route has its own Cost paragraph');
  ok(!/bollettini|postal payment slips/.test(box.innerHTML),'no postal payment slips left');
  ok(/N067/.test(panes()[1].textContent) && /pagoPA/.test(panes()[1].textContent),'the private route names the pagoPA fee');
  ok(/(Report a problem|Segnala un problema)/.test(box.textContent),'the disclaimer points to Report a problem');
  tabs()[1].click();
  ok(shown().join()==='private' && tabs()[1].getAttribute('aria-selected')==='true' && w.localStorage.getItem('patente_howto_route')==='private','the private tab switches the pane and is remembered');
  w.applyI18n();
  ok(shown().join()==='private','the choice survives a repaint of the panel');
  w.document.querySelector('details:has([data-i18n="next.summary"])')?.removeAttribute('open');
  const a=w.document.createElement('a'); a.className='exam-plan-step'; a.href='#'; w.document.body.appendChild(a); a.click();
  setTimeout(()=>{
    ok(scrolled && scrolled.classList.contains('step-theory') && scrolled.closest('.route-pane').dataset.route==='private','the ready link opens the theory-exam step of the tab showing');
    tabs()[0].click(); a.click();
    setTimeout(()=>{
      ok(scrolled && scrolled.closest('.route-pane').dataset.route==='school','and of the school tab when that one shows');
      console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
    },30);
  },30);
},2500);
