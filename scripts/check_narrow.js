// No screen is wider than a narrow phone (reported 2026-10-01 under iOS Display Zoom, which makes an iPhone 320 px wide): the dashboard with its panels open, Statistics, every Reference tab, a study card, the notes and Settings must not scroll sideways at 320 and 375 px. EXPORT= a .patente file fills the lists the way a real learner's do (the vocabulary rows that overflowed were the study list's); without it the check seeds a mock result. Needs Playwright (PLAYWRIGHT=, CHROME=). Run: node scripts/check_narrow.js
const {chromium}=require(process.env.PLAYWRIGHT||'/tmp/node_modules/playwright'); const http=require('http'),fs=require('fs'),path=require('path');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const exp=process.env.EXPORT?JSON.parse(fs.readFileSync(process.env.EXPORT,'utf8')):null;
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]); if(p==='/')p='/index.html'; const f=path.join(root,p);
 if(p==='/sw.js'){r.writeHead(404);return r.end();}
 fs.readFile(f,(e,d)=>{if(e){r.writeHead(404);return r.end();} const ext=path.extname(f); r.writeHead(200,{'Content-Type':{'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpeg':'image/jpeg'}[ext]||'application/octet-stream'}); r.end(d);});}).listen(8790, async()=>{
 const b=await chromium.launch(process.env.CHROME?{executablePath:process.env.CHROME}:{});
 let fails=0;
 for (const [W,H] of [[320,693],[375,667]]) {
 const pg=await b.newPage({viewport:{width:W,height:H}, deviceScaleFactor:2, isMobile:true, hasTouch:true});
 await pg.addInitScript((e)=>{ localStorage.setItem('patente_install_dismissed','1'); localStorage.setItem('patente_level','3'); if(!localStorage.getItem('__seeded')){ localStorage.setItem('__seeded','1'); window.__IMPORT=e; if(!e) localStorage.setItem('patente_exam_history', JSON.stringify([{date:new Date().toISOString(),correct:28,total:30,wrong:2,pass:true,level:3,items:[]}])); } }, exp);
 await pg.goto('http://localhost:8790/'); await pg.waitForTimeout(2500);
 await pg.evaluate(()=>{ if(!window.__IMPORT) return; try{ mergeDeviceState(window.__IMPORT); }catch(e){ try{ mergeProgressData(window.__IMPORT);}catch(e2){console.log(e2)} } });
 await pg.reload(); await pg.waitForTimeout(2500);
 const report=async(name)=>{ const r=await pg.evaluate(()=>{const vw=document.documentElement.clientWidth; const over=[...document.querySelectorAll('body *')].filter(e=>{const b=e.getBoundingClientRect(); return b.width>0 && b.right>vw+1 && e.offsetParent!==null;}).map(e=>e.tagName+'#'+e.id+'.'+String(e.className).slice(0,40)+' r='+Math.round(e.getBoundingClientRect().right)); return {sw:document.documentElement.scrollWidth, vw, over:over.slice(0,12)};}); const ok=r.sw<=r.vw && !r.over.length; if(!ok) fails++; console.log((ok?'ok  ':'FAIL')+' '+W+' '+name+(ok?'':' '+JSON.stringify(r))); };
 await pg.click('#nav-logo'); await pg.waitForTimeout(800); await pg.evaluate(()=>document.querySelectorAll('#screen-dashboard details').forEach(d=>d.open=true)); await report('dashboard');
 await pg.click('.nav-btn[data-screen="exam"]'); await pg.waitForTimeout(800); await report('stats');
 await pg.click('.nav-btn[data-screen="vocab"]'); await pg.waitForTimeout(1200);
 for (const sec of ['vocab','grammar','glossary','numbers','bank','weak']) { const ok=await pg.evaluate((s)=>{const b=document.querySelector(`.review-section-btn[data-section="${s}"]`); if(!b) return false; b.click(); return true;}, sec); if(ok){ await pg.waitForTimeout(900); await report('ref-'+sec); } }
 await pg.evaluate(()=>{ document.querySelectorAll('#review-pane-grammar details').forEach(d=>d.open=true); }); await report('ref-grammar-open');
 await pg.click('#nav-logo'); await pg.waitForTimeout(600);
 await pg.evaluate(()=>{ startStudySession('topic', questions[200].topic); }); await pg.waitForTimeout(1200); await report('study');
 await pg.evaluate(()=>{ openReview(questions[200].topic); }); await pg.waitForTimeout(1200); await report('review');
 await pg.evaluate(()=>{ document.getElementById('review-close-float').click(); openSettings(); }); await pg.waitForTimeout(800); await report('settings');
  await pg.close();
 }
 await b.close(); srv.close();
 console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
});
