// The driving test (20261030j, a dashboard box since 20261030s, maintainer, 2026-10-29): a page opened from the pass box, from circular
// 28819 of 2019, in the notes overlay. English for a non-Italian browser with an IT pill on every block that has an
// Italian twin, and "For American drivers" in English only; Italian alone for an Italian browser.
// Run: node scripts/check_driving_test.js (UILANG=it-IT; SRC= another public_html).
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
w.localStorage.setItem('patente_exam_date',key(-1));
w.localStorage.setItem('patente_pass_celebrated','1');
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollTo=function(){}; w.Element.prototype.scrollIntoView=function(){}; w.alert=()=>{};
w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const $=id=>w.document.getElementById(id);
setTimeout(()=>{
  w.italianoComplete=()=>true; w.renderDashboard();
  $('exam-date-box').querySelector('[data-ed=pass]').click();
  const dbox=$('dash-drivetest-box'), tbox=$('dash-topics-box');
  const tiles=dbox?[...dbox.querySelectorAll('.topic-card')]:[];
  ok(dbox && !dbox.open && dbox.querySelector('summary').textContent===(IT?'L’esame di guida':'The driving test') && dbox.nextElementSibling===w.document.querySelector('[data-i18n="next.summary"]').closest('details') && dbox.nextElementSibling.nextElementSibling===tbox,'a closed "driving test" box, then the process, then the theory box (20261030s, t)');
  ok(tiles.length===(IT?6:7) && tiles[2].textContent===(IT?'Seconda fase: le manovre':'Part 2: the maneuvers'),'one tile per section, in the reader\'s language: '+tiles.map(b=>b.textContent).join(' | '));
  ok(!$('exam-date-box').querySelector('[data-ed=drivetest]'),'the pass box no longer carries a link of its own');
  tiles[0].click();
  const body=$('review-body'), title=$('review-title').textContent, txt=body.textContent;
  ok(title===(IT?'L’esame di guida':'The driving test'),'the overlay carries the page title: '+title);
  const heads=[...body.querySelectorAll('h3')].map(h=>h.textContent);
  ok(heads.length===(IT?6:7),'six parts, and the habits in English only: '+heads.join(' | '));
  ok(IT ? /circolare 28819/.test(txt) && /frenata di precisione/.test(txt) : /circular 28819/.test(txt) && /several moves/.test(txt),'the opening names the circular, and the maneuvers are there');
  ok(IT ? !/[a-z] the [a-z]/.test(txt) && !body.querySelector('.rb-it') : true,'an Italian browser sees no English and no pills');
  if(!IT){
    const lis=[...body.querySelectorAll('[data-rb]')];
    const withPill=lis.filter(e=>e.querySelector(':scope > .rb-it')).length;
    ok(withPill===78,'every block with an Italian twin carries an IT pill: '+withPill+' of '+lis.length);
    const permit=lis.find(e=>/residence permit/.test(e.textContent)), pp=permit&&permit.querySelector(':scope > .rb-it');
    if(pp) pp.click();
    ok(!!pp && /permesso di\s+soggiorno in corso di validità/.test(pp.nextElementSibling.textContent) && /41095/.test(permit.innerHTML),'the residence permit paragraph (20261031a) cites 41095 and its pill opens its own Italian twin');
    const habits=heads.indexOf('For American drivers');
    ok(habits===6 && (body.innerHTML.slice(body.innerHTML.indexOf('For American drivers')).match(/<li/g)||[]).length===4 && !/STOP sign/.test(txt) && !/parallel parking[\s\S]*rb-it/.test(body.innerHTML.slice(body.innerHTML.indexOf('For American drivers'))),'the American section closes the page with its four points and no pill');
    const first=body.querySelector('.rb-it'); first.click();
    ok(/circolare 28819/.test(first.nextElementSibling.textContent),'the first pill opens its own Italian twin');
    ok(['Reversing (retromarcia)','Turning around (inversione di marcia)','Parking (parcheggio)','Stopping at a given point (frenata di precisione)'].every(h=>[...body.querySelectorAll('h4')].some(e=>e.textContent===h)) && /a pettine/.test(txt) && /a spina di pesce/.test(txt),'each maneuver carries the Italian name the examiner uses (20261030n)');
    const rev=[...lis].find(e=>/^Turn your head/.test(e.textContent));
    ok(rev && /Gira la testa/.test(rev.querySelector('.rb-itxt').textContent),'a step deep in the page pairs with its own twin');
  }
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
