// US equivalents on the Reference page (reviewer flag 24104, 2026-09-30): an English reader sees each length with its rounded US equivalent and one conversion note per length category; an Italian reader sees neither. The mirror row names the wrong figure 24104 uses, and the 30 cm row covers the T.A.T.S. boat (24105). Run: node scripts/check_us_units.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US'; const IT=LANG.startsWith('it');
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  w.document.querySelector('[data-screen="vocab"]')?.click();
  w.document.querySelector('.review-section-btn[data-section="numbers"]')?.click();
  const box=w.document.getElementById('review-pane-numbers')||w.document;
  const rows=[...box.querySelectorAll('.review-row')];
  const row=re=>rows.find(r=>re.test(r.textContent));
  const mirror=row(/mirror projection|specchietti oltre/i), side=row(/T\.A\.T\.S\./), tri=row(/minimum distance from outer edge|distanza minima dal bordo/i);
  const v=r=>r&&r.querySelector('.review-value').textContent;
  ok(v(mirror)===(IT?'20 cm':'20 cm (8 in)'),'mirror row value: '+v(mirror));
  ok(v(side)===(IT?'30 cm':'30 cm (12 in)'),'side projection row covers the T.A.T.S. boat, value: '+v(side));
  ok(v(tri)===(IT?'1 m':'1 m (1.1 yd)'),'triangle edge distance: '+v(tri));
  const notes=[...box.querySelectorAll('.review-group-note')].filter(p=>/US equivalents are in parentheses/.test(p.textContent));
  ok(notes.length===(IT?0:2),'conversion note on the distance and size categories only: '+notes.length);
  // Every length in meters in yards, centimeters in inches (house standard; maintainer, 2026-10-28).
  const exitRow=row(/Emergency lane usable to exit|Corsia di emergenza per uscire/), snow=row(/snowplow|sgombraneve/), ped=row(/Space left for pedestrians|transito dei pedoni/);
  ok(v(exitRow)===(IT?'500 m':'500 m (545 yd)') && v(snow)===(IT?'20 m':'20 m (22 yd)') && v(ped)===(IT?'1 m':'1 m (1.1 yd)'),'yards for every length in meters: '+[v(exitRow),v(snow),v(ped)].join(', '));
  const speed=row(/^At 130|A 130/); ok(!/\(|mph/.test(v(row(/km\/h/))||''),'speeds unchanged');
  const wr=mirror&&mirror.querySelector('.review-wrong');
  ok(wr && /50 cm/.test(wr.textContent) && (IT || /20 in/.test(wr.textContent)),'mirror row names the wrong figure, 50 cm: '+(wr&&wr.textContent));
  w.document.getElementById('review-hide').click();
  const btn=[...box.querySelectorAll('.review-row')].find(r=>/mirror projection|specchietti oltre/i.test(r.textContent)).querySelector('button.review-value');
  btn.click(); ok(btn.textContent===(IT?'20 cm':'20 cm (8 in)'),'a hidden value reveals with its equivalent: '+btn.textContent);
  w.document.getElementById('review-hide').click();
  // The same rule in the notes and the explanations: no length in meters converted to feet or miles,
  // and none in centimeters converted to anything but inches.
  // A height keeps feet and inches (maintainer, 2026-10-28), recognized by "height", "high" or "tall" shortly before or after it.
  { const bad=/\d(?:[.,]\d+)? (?:m|meters?) \([^)]*\b(ft|feet|mi|miles?|in|inch(?:es)?)\b[^)]*\)|\d cm \([^)]*\b(ft|feet|yd|yards?)\b[^)]*\)/g;
    const revs=JSON.parse(fs.readFileSync(root+'/topic_reviews.json','utf8'));
    const texts=[]; (Array.isArray(revs)?revs:Object.values(revs.reviews||revs)).forEach(r=>{ if(r&&r.en) texts.push(r.en); });
    JSON.parse(fs.readFileSync(root+'/questions.json','utf8')).forEach(q=>q.statements.forEach(s=>texts.push(s.explanation||'')));
    const hits=[]; texts.forEach(x=>{ for (const m of x.matchAll(bad)) { if (!/\b(height|high|higher|tall)\b/i.test(x.slice(Math.max(0,m.index-120),m.index+m[0].length+90))) hits.push(m[0]); } });
    ok(texts.length>7000 && hits.length===0,'notes and explanations: meters in yards except heights, centimeters in inches ('+hits.slice(0,3).join(' | ')+')'); }
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
