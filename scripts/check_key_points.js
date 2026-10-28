// The key points of every topic on one page (20261029m, maintainer, 2026-10-29): the 25 "Summary of key points"
// sections together in the notes overlay, with the IT or EN pills, a link to each topic's notes, offered under the
// dashboard's topics heading and in the exam-date box on the day before and the day of the exam.
// Run: node scripts/check_key_points.js (UILANG=it-IT; SRC= another public_html).
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
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollTo=function(){}; w.Element.prototype.scrollIntoView=function(){}; w.alert=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
const $=id=>w.document.getElementById(id);
const vis=el=>el&&!el.classList.contains('hidden');
setTimeout(()=>{
  w.renderDashboard();
  const link=$('dash-keypoints');
  ok(vis(link) && /(Key points of every topic|Punti chiave di ogni argomento), .*(\d+) (minutes|minuti)/.test(link.textContent),'the dashboard offers the page with a reading time: '+link.textContent);
  const mins=Number(link.textContent.match(/(\d+) (minutes|minuti)/)[1]);
  ok(mins>=15 && mins<=40,'the reading time is a short one: '+mins);
  link.querySelector('button').click();
  const ov=$('review-overlay'); const body=$('review-body');
  ok(vis(ov) && $('review-title').textContent===(IT?'Punti chiave di ogni argomento':'Key points of every topic'),'it opens in the notes overlay under its own title');
  const h2=[...body.querySelectorAll('h3')];
  ok(h2.length===25,'one heading per topic: '+h2.length);
  const order=w.topicsInStudyOrder();
  ok(h2[0].textContent===w.eval('TOPIC_SHORT')[order[0]][w.eval('reviewLang')] && h2[24].textContent===w.eval('TOPIC_SHORT')[order[24]][w.eval('reviewLang')],'the topics are in study order, under their short names');
  const lis=body.querySelectorAll('li').length;
  ok(lis>=100,'the numbered points are there: '+lis);
  ok(!body.querySelector('img'),'no figures');
  const notes=body.querySelectorAll('.kp-notes');
  ok(notes.length===25 && notes[4].dataset.topic===order[4],'each topic carries a link to its full notes');
  const lang=w.eval('reviewLang');
  if (IT) {
    ok(lang==='it' && !body.querySelector('.rb-it') && !vis($('review-lang')),'an Italian browser reads it in Italian, with no pills and no toggle');
  } else {
    ok(lang==='it' && vis($('review-lang')),'at Italiano the page opens in Italian with the toggle');
    const pills=body.querySelectorAll('.rb-it').length;
    ok(pills>=lis-5,'nearly every point carries an EN pill: '+pills+' of '+lis);
    w.document.querySelector('#review-lang [data-lang=en]').click();
    const en=$('review-body'); const enLis=en.querySelectorAll('li').length, enPills=en.querySelectorAll('.rb-it').length;
    ok(w.eval('reviewLang')==='en' && en.querySelectorAll('h3').length===25 && enPills>=enLis-5,'the English face has IT pills on nearly every point: '+enPills+' of '+enLis);
    // The Italian key words in parentheses (20261029n): nearly every point with a bold run carries one
    const items=[...en.querySelectorAll('li')]; const bold=items.filter(l=>l.querySelector('strong')); const withIt=bold.filter(l=>/\(\s*$/.test('') || /\(/.test(l.textContent) && l.querySelector('strong + em, strong ~ em'));
    const first=en.querySelector('li strong'); const par=first && first.nextSibling && first.nextSibling.textContent;
    ok(bold.length>=150 && withIt.length>=bold.length-8,'the English points carry the Italian key words in parentheses: '+withIt.length+' of '+bold.length);
    ok(/^ \($/.test(par||'') && first.nextElementSibling && first.nextElementSibling.tagName==='EM' && /[a-zà-ù]/.test(first.nextElementSibling.textContent),'a bold key word is followed by its Italian in italics: '+first.textContent+' ('+(first.nextElementSibling&&first.nextElementSibling.textContent)+')');
    const li=en.querySelector('li .rb-it'); const twin=li.nextElementSibling;
    ok(twin && twin.classList.contains('rb-itxt') && /[àèìòù]/.test(twin.textContent),'a pill reveals Italian');
  }
  $('review-body').querySelectorAll('.kp-notes')[4].click();
  ok($('review-title').textContent===w.topicShort(order[4]) && body.querySelectorAll('h3').length>1,'the notes link opens that topic\'s full notes');
  w.dismissReview();
  // the exam-date box: the link on the day before and the day itself, not a week out
  w.italianoComplete=()=>true;
  w.localStorage.setItem('patente_exam_date',key(1)); w.renderDashboard();
  ok(!!$('exam-date-box').querySelector('[data-ed=keypoints]'),'the exam-date box offers it the day before');
  w.localStorage.setItem('patente_exam_date',key(0)); w.renderDashboard();
  const kb=$('exam-date-box').querySelector('[data-ed=keypoints]');
  ok(!!kb,'and on the day itself');
  kb.click(); ok(vis(ov) && body.querySelectorAll('h3').length===25,'the link opens the page'); w.dismissReview();
  w.localStorage.setItem('patente_exam_date',key(6)); w.renderDashboard();
  ok(!$('exam-date-box').querySelector('[data-ed=keypoints]'),'not six days out, where the box asks for the review');
  ok(!(w.eval('KEY_POINTS') in w.eval('topicReviews')),'the page is not a topic in topicReviews');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
