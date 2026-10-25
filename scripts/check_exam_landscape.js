// The mock exam sheet fits the window, landscape phones and short portrait ones included (reported 2026-10-01, twice): the longest statement and the busiest figure, at three landscape phone sizes, three short portrait ones (Display Zoom, an SE), a portrait phone and a laptop, must leave the strip on screen with no page scroll. Needs Playwright (PLAYWRIGHT=path to the package, CHROME=path to a Chromium binary). Run: node scripts/check_exam_landscape.js
const {chromium}=require(process.env.PLAYWRIGHT||'/tmp/node_modules/playwright'); const http=require('http'),fs=require('fs'),path=require('path');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]); if(p==='/')p='/index.html'; const f=path.join(root,p);
 if(p==='/sw.js'){r.writeHead(404);return r.end();}
 fs.readFile(f,(e,d)=>{if(e){r.writeHead(404);return r.end();} const ext=path.extname(f); r.writeHead(200,{'Content-Type':{'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpeg':'image/jpeg','.jpg':'image/jpeg'}[ext]||'application/octet-stream'}); r.end(d);});}).listen(8771, async()=>{
 const b=await chromium.launch(process.env.CHROME?{executablePath:process.env.CHROME}:{});
 let fails=0;
 const sizes=(process.env.SIZES||'667x375,844x390,932x430,320x650,320x693,375x667,390x844,1280x800').split(',');
 for (const mode of ['long','detailed']) for (const sz of sizes){ const [W,H]=sz.split('x').map(Number);
  const pg=await b.newPage({viewport:{width:W,height:H}, colorScheme:'light', deviceScaleFactor:2, isMobile: W<1000, hasTouch: W<1000});
  await pg.addInitScript((m)=>{window.__MODE=m;localStorage.setItem('patente_level','3');localStorage.setItem('patente_install_dismissed','1');}, mode);
  await pg.goto('http://localhost:8771/'); await pg.waitForTimeout(2000);
  const res=await pg.evaluate((fig)=>{window.italianoComplete=()=>true;window.difficultCards=()=>[];renderDashboard();document.getElementById('btn-dash-mock').click();document.getElementById('mock-intro-start').click();
    const mode=window.__MODE; let pick;
    if(mode==='detailed'){ const q=questions.filter(q=>IMG_DETAILED.has(q.image)).sort((a,b)=>b.statements.reduce((m,s)=>Math.max(m,s.italian_text.length),0)-a.statements.reduce((m,s)=>Math.max(m,s.italian_text.length),0))[0]; const st=q.statements.slice().sort((a,b)=>b.italian_text.length-a.italian_text.length)[0]; pick={q,stmt:st}; }
    else { let best=null; for(const q of questions) for(const st of q.statements) if(!best||st.italian_text.length>best.stmt.italian_text.length) best={q,stmt:st}; pick=best; }
    examState.items[0]=pick; goExamStatement(0);
    return 0;}, !!process.env.FIG);
  await pg.waitForTimeout(700);
  const m=await pg.evaluate(()=>{const sh=document.getElementById('exam-sheet').getBoundingClientRect(); return {top:Math.round(sh.top), bottom:Math.round(sh.bottom), vh:innerHeight, scroll:document.documentElement.scrollHeight};});
  // In a tall window (760 px or more) a detailed board keeps its 400 px floor and the page scrolls, by design (CLAUDE.md, the mock sheet); shorter windows, landscape or portrait (Display Zoom, an SE), must fit whatever the figure.
  const okk=(m.bottom<=m.vh && m.scroll<=m.vh) || (mode==='detailed' && m.vh>=760);
  console.log((okk?'ok  ':'FAIL')+' '+mode+' '+sz+' '+JSON.stringify(m)); if(!okk) fails++;
  await pg.close();
 }
 await b.close(); srv.close();
 console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
});
