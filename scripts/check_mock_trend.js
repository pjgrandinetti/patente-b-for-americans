// Advice from the learner's own mocks, and the mock exam trend (maintainer, 2026-10-02): the lean line (ten or more mistakes, two to one), the spare-time sentence, the 'When you do not fully understand the Italian' part (never for an Italian browser), the length line, and two charts of the mocks by count with the effort in mocks. Run: node scripts/check_mock_trend.js (UILANG=it-IT).
const {JSDOM}=require(process.env.JSDOM||'/tmp/node_modules/jsdom'); const fs=require('fs');
const root=process.env.SRC||require('path').resolve(__dirname,'../public_html');
const LANG=process.env.UILANG||'en-US';
let html=fs.readFileSync(root+'/index.html','utf8').replace(/<script[^>]*src="app\.js[^>]*><\/script>/,'');
const dom=new JSDOM(html,{url:'https://patente.physyapps.com/',runScripts:'dangerously',pretendToBeVisual:true});
const w=dom.window; Object.defineProperty(w.navigator,'language',{value:LANG}); Object.defineProperty(w.navigator,'languages',{value:[LANG]});
w.localStorage.setItem('patente_level','3');
w.fetch=async(u)=>{const p=root+'/'+String(u).replace(/^https:\/\/patente\.physyapps\.com\//,'').replace(/\?.*$/,'');return{ok:true,status:200,json:async()=>JSON.parse(fs.readFileSync(p,'utf8')),text:async()=>fs.readFileSync(p,'utf8')}};
w.scrollTo=()=>{}; w.Element.prototype.scrollIntoView=()=>{}; w.Element.prototype.scrollTo=()=>{}; w.matchMedia=()=>({matches:false,addEventListener(){},addListener(){}});
w.speechSynthesis={getVoices:()=>[],cancel(){},speak(){}}; w.SpeechSynthesisUtterance=class extends w.EventTarget{};
const s=w.document.createElement('script'); s.textContent=fs.readFileSync(root+'/app.js','utf8'); w.document.body.appendChild(s);
const IT=LANG.startsWith('it');
let fails=0; const ok=(c,m)=>{console.log((c?'ok  ':'FAIL')+' '+m); if(!c)fails++;};
setTimeout(()=>{
  const qs=w.eval('questions'); const pool=[]; for(const q of qs) for(const st of q.statements) pool.push({q,st});
  const F=pool.filter(x=>x.st.answer==='FALSO'), V=pool.filter(x=>x.st.answer==='VERO');
  // wrongs newest first; fa = how many of each sheet's mistakes are false statements marked true
  const sheet=(i,wrong,fa,time)=>{ const items=[]; let f=0,v=0;
    for(let k=0;k<30;k++){ const miss=k<wrong; const useF=miss?(k<fa):(k%2===0); const x=useF?F[i*40+f++]:V[i*40+v++];
      items.push({id:x.q.id,n:String(x.st.number),chosen:miss?(x.st.answer==='VERO'?'FALSO':'VERO'):x.st.answer,s:15}); }
    return {date:new Date(Date.UTC(2026,9,2,18)-i*3600e3).toISOString(),correct:30-wrong,total:30,wrong,pass:wrong<=3,level:3,time,items}; };
  const set=h=>{w.localStorage.setItem('patente_exam_history',JSON.stringify(h)); w.updateExamAvailability();};
  const $=id=>w.document.getElementById(id);
  w.document.querySelector('.nav-btn[data-screen="exam"]').click();
  // The maintainer's fifteen of 2026-10-02: 25 mistakes, 17 of them false statements marked true.
  const wr=[1,2,1,1,3,2,1,1,3,2,0,4,2,2,0], fa=[1,1,1,1,2,2,1,0,2,1,0,3,1,1,0];
  set(wr.map((x,i)=>sheet(i,x,fa[i],540)));
  const lean=$('exam-lean-note');
  ok(lean && !lean.classList.contains('hidden') && /\b25\b/.test(lean.textContent) && /\b17\b/.test(lean.textContent) && /(false statements you marked true|false che hai segnato come vere)/.test(lean.textContent),'the lean line: '+lean.textContent);
  ok(/(go back to the questions you doubted|tornare alle domande)/.test($('exam-time-note').textContent),'finishing in under half the time: the spare-time sentence');
  set(wr.map((x,i)=>sheet(i,x,fa[i],900))); ok(!/(go back to|tornare alle)/.test($('exam-time-note').textContent),'at 30 seconds a question it is not said');
  set(wr.slice(0,3).map((x,i)=>sheet(i,x,x,540))); ok($('exam-lean-note').classList.contains('hidden'),'four mistakes: no lean line');
  set(wr.map((x,i)=>sheet(i,x,Math.ceil(x/2),540))); ok($('exam-lean-note').classList.contains('hidden'),'an even split: no lean line');
  set(wr.map((x,i)=>sheet(i,x,0,540))); ok(/(true statements you marked false|vere che hai segnato come false)/.test($('exam-lean-note').textContent),'the other lean is named too');
  // Strategies: the reading part and the length line.
  const g=$('exam-guess');
  if(IT){ ok(!g.querySelector('.strat-read') && !/When you do not fully understand/.test(g.textContent),'an Italian browser gets no reading advice'); }
  else { ok(g.querySelectorAll('.strat-read li').length===5 && /When you do not fully understand the Italian/.test(g.textContent),'five steps under their heading');
    let opened=null; const o=w.openGrammarTopic; w.openGrammarTopic=id=>{opened=id;}; g.querySelector('.strat-grammar-link').click(); w.openGrammarTopic=o;
    ok(opened==='parse','the link opens Taking a statement apart');
    w.openGrammarTopic('parse'); ok(w.eval('reviewSection')==='grammar' && w.document.querySelector('details.gr-topic[data-gr="parse"]')?.open,'and the Grammar tab shows that topic open');
    w.document.querySelector('.nav-btn[data-screen="exam"]').click(); }
  const len=w.document.querySelector('#exam-guess .strat-length').textContent.match(/\d+/g).map(Number);
  ok(len.length===4 && len[0]===12 && len[2]===23 && len[1]>=55 && len[3]>=55,'the length line, computed from the bank: '+len.join(', '));
  // The trend box.
  set(wr.map((x,i)=>sheet(i,x,fa[i],540)));
  const tr=$('exam-trend');
  ok(tr && !tr.classList.contains('hidden') && !tr.querySelector('details') && tr.nextElementSibling===$('stats-mock-row') && $('stats-mock-row').nextElementSibling===$('exam-history') && /^(Mock exam trend|Andamento delle simulazioni)$/.test(tr.querySelector('h2').textContent),'open at the top, right above the readiness ring, not in a disclosure');
  ok($('exam-readiness-top').nextElementSibling===tr && $('exam-readiness-top').contains($('readiness-ring-wrap')) && !$('exam-readiness-top').classList.contains('hidden'),'the readiness ring heads the page, above the trend');
  const hb=$('exam-history-box'); ok(hb && hb.tagName==='DETAILS' && !hb.open && hb.contains($('exam-history-table')) && /\(15\)/.test(hb.querySelector('summary').textContent) && !hb.contains($('readiness-ring-wrap')),'the table is in a closed disclosure, Past results (15), with the ring outside it');
  ok(!tr.querySelector('.trend-effort') && !/(another \d+ mock|altre \d+ simulazioni|average of about|media di circa)/.test(tr.textContent),'no count of further mocks and no needed average above the chart (20261009w)');
  const svgs=[...tr.querySelectorAll('svg.trend-svg')];
  { const cls=k=>svgs[0].querySelectorAll('.tc-dot.'+k).length; // mocks 3 to 15 of wr: 2,0,1,1,2,3,1,1,2,1,1,2,1 -> wrongs oldest-first
    const shownW=wr.slice().reverse().slice(2); const exp={p:shownW.filter(x=>x<3).length,e:shownW.filter(x=>x===3).length,f:shownW.filter(x=>x>3).length};
    ok(cls('is-pass')===exp.p && cls('is-edge')===exp.e && cls('is-fail')===exp.f,'dots colored by result: '+cls('is-pass')+' passed, '+cls('is-edge')+' at 27, '+cls('is-fail')+' failed'); }
  ok($('stats-mock-row') && $('exam-trend').nextElementSibling===$('stats-mock-row') && $('stats-mock-row').contains($('btn-stats-mock')),'Take another mock exam sits right below the trend');
  ok(svgs.length===1 && svgs[0].querySelectorAll('.tc-dot').length===13,'one chart; thirteen dots, the third mock to the fifteenth');
  // The axis carries dates, one at the first mock of each day (20261024d): the seed's fifteen mocks sit an hour apart, so they span one or two days
  const xt=[...svgs[0].querySelectorAll('.tc-tick')].filter(e=>e.getAttribute('text-anchor')==='middle').map(e=>e.textContent);
  ok(xt.length>=1 && xt.length<=2 && xt.every(x=>/[A-Za-z]/.test(x) && !/^\d+$/.test(x)),'the axis shows dates, not counts, one per day: '+xt.join(' | '));
  ok(/(Date of each mock exam|Data di ogni simulazione)/.test(svgs[0].querySelector('.tc-axis').textContent),'the axis caption names the date');
  // The axis choice (20261024f): by date is the default, by count brings the mock numbers back, and the choice is kept on the device
  { const btns=[...tr.querySelectorAll('.trend-axis-btn')]; ok(btns.length===2 && btns[0].dataset.axis==='time' && btns[0].classList.contains('active'),'two axis buttons, By date active by default');
    btns[1].click(); const xt2=[...tr.querySelectorAll('.tc-tick')].filter(e=>e.getAttribute('text-anchor')==='middle').map(e=>e.textContent);
    ok(xt2[0]==='3' && xt2[xt2.length-1]==='15' && /(Mock exam number|Numero della simulazione)/.test(tr.querySelector('.tc-axis').textContent) && w.localStorage.getItem('patente-trend-axis')==='count','By count: the axis runs from mock 3 to mock 15 and the choice is stored: '+xt2.join(' '));
    tr.querySelector('.trend-axis-btn[data-axis=time]').click(); ok(tr.querySelector('.trend-axis-btn[data-axis=time]').classList.contains('active'),'By date again'); }
  // Linear in time (20261024e): with mocks at 0, 1 and 3 hours, the second sits a third of the way, not half
  { const sc=w.trendXScale(400,{n:3,x0:1,xs:[null,0,3600e3,3*3600e3],refs:[]}); const a=sc.X(1), m=sc.X(2), z=sc.X(3);
    ok(Math.abs((m-a)/(z-a)-1/3)<1e-9,'the horizontal scale is linear in time: a mock an hour in sits a third of the way along a three-hour span'); }
  { const cx=[...svgs[0].querySelectorAll('.tc-dot')].map(e=>+e.getAttribute('cx')); const gaps=cx.slice(1).map((v,i)=>v-cx[i]);
    ok(gaps.every(g=>Math.abs(g-gaps[0])<0.6),'the seed\'s mocks, an hour apart, are evenly spaced: '+gaps.map(g=>g.toFixed(1)).join(' ')); }
  const rows=w.mockTrendData();
  ok(rows.length===15 && rows[0].wrong===0 && rows[14].wrong===1 && Math.abs(rows[14].mean-25/15)<1e-9,'oldest first; the last average is 25/15');
  ok(Math.abs(rows[14].sd-w.mockRecentForm().sObs)<1e-9 && Math.abs(rows[14].chance-w.mockRecentForm().s)<1e-9 ,'the spread and the chance level are the prediction\'s own');
  ok(svgs[0].querySelectorAll('.tc-ref').length===1,'one level on the first chart: the pass line');
  const ref=[[3,0.68,0.7387004358795557,2.3948857816433815],[3,0.95,0.5206582666988173,6.28473469648538],[5,0.68,0.7798561168940737,1.6759594785234726]];
  ok(ref.every(([n,p,lo,hi])=>{const r=w.sdRange(1,n,p); return Math.abs(r.lo-lo)<1e-6 && Math.abs(r.hi-hi)<1e-6;}),'sdRange agrees with scipy to 1e-6');
  ok(!/standard deviation|deviazione standard/i.test(tr.querySelector('.trend-charts').textContent),'no standard deviation chart');
  ok(/(raise your average score|alza la media)/.test(tr.querySelector('.trend-verdict').textContent) && !/(random|drawn|estratt|caso)/i.test(tr.textContent),'steady scores: raise the average, with no talk of random draws');
  // The next score's range: mean ± t(0.95, n−1)·s·√(1+1/n); its edge is the banner's own test.
  const f=w.mockRecentForm(), nx=rows[14].next;
  ok(Math.abs(w.tQuantile(0.84,14)-1.0310531)<1e-5 && Math.abs(w.tQuantile(0.95,14)-1.7613101)<1e-5,'tQuantile agrees with scipy');
  ok(Math.abs((nx.hi-nx.lo)/2-1.7613101*f.s*Math.sqrt(1+1/15))<1e-5 && Math.abs((nx.hi+nx.lo)/2-f.mean)<1e-9,'the range of the next score: mean ± t·s·√(1+1/n)');
  ok((30-nx.hi<26.5)===(f.chance<0.95) && 30-nx.hi<27,'not ready (chance '+f.chance.toFixed(3)+'): the band reaches below the pass line, lower edge '+(30-nx.hi).toFixed(2));
  ok(svgs[0].querySelectorAll('polygon.tc-band').length===1 && rows[1].next===null && rows[2].next && (rows[2].next.hi-rows[2].next.lo)>(nx.hi-nx.lo),'one band, from the third mock, narrowing with more mocks');
  ok(/(every score in the range is 27 or more\. The range now starts at 26\.|ogni punteggio dell’intervallo è 27 o più\. Ora l’intervallo parte da 26\.)/.test(tr.querySelector('.trend-band-note').textContent) && !/\d[.,]\d/.test(tr.querySelector('.trend-band-note').textContent),'the note speaks in whole scores: '+tr.querySelector('.trend-band-note').textContent);
  ok(/(raise your average score|alza la media)/.test(tr.querySelector('.trend-verdict').textContent) && !/(random|drawn|estratt|caso)/i.test(tr.textContent),'steady scores: raise the average, with no talk of random draws');
  ok(tr.querySelectorAll('.trend-legend .trend-key').length===6,'the chart has its legend');
  const ticks=i=>[...svgs[i].querySelectorAll('.tc-tick')].filter(e=>e.getAttribute('text-anchor')==='end').map(e=>e.textContent);
  const lows=rows.filter(r=>r.next).map(r=>30-r.next.hi); ok(+ticks(0)[0]<=Math.min(...lows) && +ticks(0)[0]<26,'the scale reaches the lowest edge the band has had: from '+ticks(0)[0]+' (lowest edge '+Math.min(...lows).toFixed(1)+')');
  ok(ticks(0).every(x=>/^\d+$/.test(x)) && ticks(0)[ticks(0).length-1]==='30','whole ticks up to 30: '+ticks(0).join(' '));
  const cy=[...svgs[0].querySelectorAll('.tc-dot')].map(e=>+e.getAttribute('cy')); ok(cy[2]<cy[1],'a perfect mock (the fifth) is drawn above a mock with 4 wrong (the fourth)');
  w.updateExamAvailability(); ok($('exam-trend').querySelectorAll('svg').length===1,'it is drawn again when the page redraws');
  // A tap on a dot opens that mock's exam below (20261010k).
  { const svg=$('exam-trend').querySelector('svg.trend-svg'); const W=+svg.getAttribute('width'), L=+svg.dataset.l, R=+svg.dataset.r, n=+svg.dataset.n, x0=+svg.dataset.x0;
    svg.getBoundingClientRect=()=>({left:0,top:0,width:W,height:190});
    const tapAt=i=>svg.dispatchEvent(new w.MouseEvent('click',{bubbles:true,clientX:L+(i-x0)/(n-x0)*(W-L-R),clientY:50}));
    const hb=$('exam-history-box'); hb.open=false;
    tapAt(n); const panel=$('exam-history-review');
    ok(!hb.open && panel && !panel.classList.contains('hidden') && panel.dataset.idx==='0' && hb.nextElementSibling===panel,'the newest dot opens the newest exam, just under the Past results box, which stays closed');
    ok($('exam-history-table').querySelector('tr.is-open')?.dataset.idx==='0' && $('exam-trend').querySelectorAll('.tc-dot.is-open').length===1 && $('exam-trend').querySelector('.tc-dot.is-open').dataset.h==='0','its row is marked and its dot ringed');
    tapAt(n-4); ok(panel.dataset.idx==='4' && $('exam-trend').querySelector('.tc-dot.is-open').dataset.h==='4','another dot opens its own exam: '+panel.dataset.idx);
    tapAt(n-4); ok(panel.classList.contains('hidden') && !$('exam-trend').querySelector('.tc-dot.is-open'),'a second tap closes it');
    svg.dispatchEvent(new w.MouseEvent('pointermove',{bubbles:true,clientX:L+(W-L-R)/2,clientY:50}));
    ok(/(Tap or click to see this exam below|Tocca o fai clic per vedere questa simulazione)/.test($('exam-trend').querySelector('.trend-tip').textContent),'the tooltip says so'); }
  set([1,1,0,1,1,2,0,1,1].map((x,i)=>sheet(i,x,x,540))); ok(!$('exam-trend').querySelector('.trend-effort'),'nine good mocks: still no prediction line');
  set([1,0,1,1,0,2,1,0,1,1,0,1,1,0,1].map((x,i)=>sheet(i,x,x,540))); ok(/(meet the 5% target|raggiungono l’obiettivo del 5%)/.test(($('exam-trend').querySelector('.trend-effort')||{}).textContent||''),'fifteen at the bar: the line says the target is met');
  set([0,6,0,7,1,0,6,0,5,0].map((x,i)=>sheet(i,x,x,540))); 
  ok(/(vary a lot|variano molto)/.test($('exam-trend').querySelector('.trend-verdict').textContent),'erratic results: steadier scores');
  { const good=[1,0,1,1,0,2,1,0,1,1,0,1,1,0,1]; set(good.map((x,i)=>sheet(i,x,x,540)));
    const r=w.mockTrendData()[14]; ok(w.mockRecentForm(15,15).chance>=0.95 && 30-r.next.hi>=26.5 && !$('exam-trend').querySelector('.trend-band-note') && !$('exam-trend').querySelector('.trend-verdict'),'at the banner\'s bar the whole band clears the pass line, and no note is drawn'); }
  { const band=()=>(($('exam-trend').querySelector('.trend-swatch.is-band')||{}).parentElement||{}).textContent||'';
    const num=x=>Number(String(x).replace(',','.'));
    const parse=()=>{ const m=band().match(/^(\d+(?:[.,]\d+)?)% (?:chance your next score is|di probabilità che il prossimo punteggio sia tra) (\d+) (?:to|e) (\d+)$/); return m&&{pct:num(m[1]),lo:+m[2],hi:+m[3]}; };
    // the share of a whole-score range, straight from the t, as a check on the app's arithmetic
    const shareOf=(nx,lo,hi)=>{ const at=x=>w.studentT((x-(30-nx.mean))/nx.se,nx.df); return (hi>=30?1:at(hi+0.5))-at(lo-0.5); };
    // (1) A learner at the bar whose range is 27 to 30: the share is the chance of passing, and the two figures add to 100.
    set([1,1,1,2,1,1,1,1,2,1,1,1,1,1,1].map((x,i)=>sheet(i,x,x,540)));
    let b=parse(), f=w.mockRecentForm();
    ok(b && b.lo===27 && b.hi===30 && Math.abs(b.pct+num(w.failPctText(f.chance))-100)<1e-9,'27 to 30 quotes the chance of passing, adding to 100 with the chance of failing ('+w.failPctText(f.chance)+'%): '+band());
    // (2) A range ending at 30 from a higher score: its share comes from the same t.
    set([1,0,1,1,0,2,1,0,1,1,0,1,1,0,1].map((x,i)=>sheet(i,x,x,540)));
    b=parse(); let nx=w.mockTrendData()[14].next;
    ok(b && b.hi===30 && b.lo===Math.round(30-nx.hi) && Math.abs(b.pct-(100-num(w.failPctText(shareOf(nx,b.lo,30)))))<1e-9,'a range ending at 30 quotes its own chance: '+band());
    // (3) A range ending below 30: both edges priced.
    set([5,6,4,5,6,5,4,5,6,5].map((x,i)=>sheet(i,x,x,540)));
    b=parse(); nx=w.mockTrendData()[9].next;
    ok(b && b.hi<30 && Math.abs(b.pct-(100-num(w.failPctText(shareOf(nx,b.lo,b.hi)))))<1e-9 && b.pct>85 && b.pct<97,'a range ending below 30 quotes its own chance, near the band\'s 90: '+band()); }
  set([1,0,2].map((x,i)=>sheet(i,x,x,540))); ok($('exam-trend').classList.contains('hidden'),'three mocks: no trend box');
  set([1,0,2,1].map((x,i)=>sheet(i,x,x,540))); ok(!$('exam-trend').classList.contains('hidden'),'four mocks: the box appears');
  console.log(fails?`${fails} FAILED`:'all passed'); process.exit(fails?1:0);
},2500);
