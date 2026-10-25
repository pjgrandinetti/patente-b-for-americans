// The 📖 lands on the card's own drawing when the review carries it, even
// when the statement is claimed by a paragraph in the same topic; a claim in
// another topic still wins, and a card without its drawing keeps the claim.
// Run: node scripts/check_book_landing.js (SRC=, JSDOM=).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:'en-US'});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}}); w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  const T=n=>w.eval(`(()=>{const q=questions.find(q=>q.statements.some(s=>s.number==='${n}'));const t=reviewTargetFor(q,'${n}');return t&&{img:t.scrollToImage||null,blk:!!t.scrollToBlock,topic:t.topic||q.topic,own:q.topic};})()`);
  const a=T('23161'); ok(a&&a.img&&/4459/.test(a.img),'23161 opens at its drawing: '+JSON.stringify(a));
  const b=T('24106'); ok(b&&!b.img&&b.topic!==b.own,'24106 keeps its claim in another topic: '+JSON.stringify(b));
  // a claimed statement whose card has no drawing in the review
  const n=w.eval(`(()=>{for(const q of questions){if(reviewImageFor(q.topic,q,true))continue;for(const s of q.statements){const c=reviewClaims[s.number];if(c&&c.topic===q.topic)return s.number;}}})()`);
  const c=T(n); ok(c&&!c.img&&c.blk,'a card without its drawing in the review keeps the claim ('+n+')');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
