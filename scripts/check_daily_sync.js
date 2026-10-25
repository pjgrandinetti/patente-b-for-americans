// Today's count adds up across devices, and the average stays on screen once
// every level is cleared (maintainer, 2026-09-30). Two jsdom windows as two
// devices; sync is modelled by handing one's bundle to the other's
// mergeDeviceState. Run: node scripts/check_daily_sync.js (SRC=app.js to test another build).
const fs = require('fs');
// jsdom: `npm install jsdom` anywhere on the module path, or into /tmp.
let JSDOM; try { ({ JSDOM } = require('jsdom')); } catch { ({ JSDOM } = require('/tmp/node_modules/jsdom')); }
const PUB = require('path').join(__dirname, '..', 'public_html') + '/';
const html = fs.readFileSync(PUB + 'index.html', 'utf8').replace(/<script[^>]*src="app\.js"[^>]*><\/script>/, '');
const SRC = fs.readFileSync(process.env.SRC || (PUB + 'app.js'), 'utf8');
let pass = 0, fail = 0; const ck = (c, m) => { if (c) pass++; else { fail++; console.log('  ✗', m); } };
const wait = ms => new Promise(r => setTimeout(r, ms));
function boot() {
  const dom = new JSDOM(html, { runScripts: 'dangerously', url: 'https://patente.physyapps.com/', pretendToBeVisual: true });
  const w = dom.window;
  const u = require('util'); w.TextEncoder = u.TextEncoder; w.TextDecoder = u.TextDecoder;
  Object.defineProperty(w, 'crypto', { value: require('crypto').webcrypto, configurable: true });
  w.__postGate = null; w.__posted = [];
  w.fetch = async (url, opt) => {
    const s = String(url);
    if (s.includes('submit-flags.php')) {
      w.__posted.push(JSON.parse(opt.body).flags.map(f => f.number));
      if (w.__postGate) await w.__postGate;
      return { ok: true, status: 200, json: async () => ({ ok: true }) };
    }
    const f = s.replace(/^https?:\/\/[^/]+\//, '').replace(/^\//, '').split('?')[0];
    const b = fs.readFileSync(PUB + f); return { ok: true, status: 200, json: async () => JSON.parse(b), text: async () => b.toString() };
  };
  w.scrollTo = () => {}; w.HTMLElement.prototype.scrollIntoView = function () {};
  w.localStorage.setItem('patente_dev', '1');
  const sc = w.document.createElement('script'); sc.textContent = SRC; w.document.body.appendChild(sc);
  return w;
}
const flag = (w, n, ts) => w.eval(`addOrUpdateFlag({ number: ${n}, category: 'explanation', note: 'n${n}', answer: 'VERO', ts: ${ts} })`);
const day = w => w.loadDaily()[w.dayKey()] || {};
const sync = (from, to) => to.mergeDeviceState(JSON.parse(JSON.stringify(from.buildProgressBundle())));
(async () => {
  const A = boot(), B = boot();
  await wait(2500);
  // Each device records its own answers today: A 3 correct drill answers, B 2.
  for (let i = 0; i < 3; i++) A.dailyRecordAnswer(true, [], true);
  for (let i = 0; i < 2; i++) B.dailyRecordAnswer(true, [], true);
  sync(A, B); sync(B, A);
  ck(day(A).w === 5 && day(B).w === 5, `drill answers from two devices ADD UP (A ${day(A).w}, B ${day(B).w}, want 5)`);
  ck(day(A).a === 5 && day(B).a === 5, 'answers add up too');
  ck(A.todayProgress() === 5 && B.todayProgress() === 5, 'Today reads 5 on both devices');
  sync(A, B); sync(B, A);
  ck(day(A).w === 5 && day(B).w === 5, 'syncing again does not double the count');
  A.dailyRecordAnswer(true, [], true); sync(A, B);
  ck(day(B).w === 6, 'a later answer on A arrives on B');
  // An older build sends totals only, which may already hold this device's answers.
  const old = {}; old[A.dayKey()] = { a: 6, c: 6, w: 6, m1: 0, m2: 0, m3: 0 };
  A.mergeDaily(old);
  ck(day(A).w === 6, 'an old build\'s total is a floor, not added');
  const old2 = {}; old2[A.dayKey()] = { a: 9, c: 9, w: 9 };
  A.mergeDaily(old2);
  ck(day(A).w === 9, 'a larger old total raises the floor');
  // A day recorded before per-device counts keeps its totals.
  const L = {}; L[A.dayKeyOffset(3)] = { a: 40, c: 35, m1: 20, m2: 0, m3: 0 };
  A.localStorage.setItem('patente_daily', JSON.stringify(Object.assign(A.loadDaily(), L)));
  A.dailyRecordTime(5000); // writes today only
  ck(A.loadDaily()[A.dayKeyOffset(3)].m1 === 20, 'an old-format day keeps its totals');
  const L2 = {}; L2[A.dayKeyOffset(3)] = { a: 40, c: 35, m1: 20 };
  B.mergeDaily(L2); B.mergeDaily(L2);
  ck(B.loadDaily()[B.dayKeyOffset(3)].m1 === 20, 'an old-format day merged twice stays at its total');
  // Every level cleared: the average line is still drawn.
  const seed = {}; for (let i = 1; i <= 5; i++) seed[A.dayKeyOffset(i)] = { a: 30, c: 25, w: 20, m1: 0, m2: 0, m3: 0 };
  A.localStorage.setItem('patente_daily', JSON.stringify(seed));
  A.remainingAcrossLevels = () => 0;
  A.renderDailyLoop();
  const txt = A.document.getElementById('daily-projection').textContent;
  ck(/average of 20 correct answers|media di 20 risposte/.test(txt), 'with every level cleared the average line shows: ' + txt.slice(0, 160));
  console.log(fail ? `${fail} FAILED, ${pass} passed` : `all ${pass} passed`); process.exit(fail ? 1 : 0);
})();
