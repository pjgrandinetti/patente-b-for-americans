// A reviewer's unsaved comment survives leaving the card (bug report
// 2026-09-28). Run: node scripts/check_flag_draft.js (SRC= another app.js).
const fs = require('fs');
let JSDOM; try { ({ JSDOM } = require('jsdom')); } catch { ({ JSDOM } = require('/tmp/node_modules/jsdom')); }
const PUB = require('path').join(__dirname, '..', 'public_html') + '/';
const html = fs.readFileSync(PUB + 'index.html', 'utf8').replace(/<script[^>]*src="app\.js"[^>]*><\/script>/, '');
const SRC = fs.readFileSync(process.env.SRC || (PUB + 'app.js'), 'utf8');
let pass = 0, fail = 0; const ck = (c, m) => { if (c) pass++; else { fail++; console.log('  ✗', m); } };
const wait = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const dom = new JSDOM(html, { runScripts: 'dangerously', url: 'https://patente.physyapps.com/', pretendToBeVisual: true });
  const w = dom.window;
  w.fetch = async (url) => { const f = String(url).replace(/^https?:\/\/[^/]+\//, '').replace(/^\//, '').split('?')[0];
    const b = fs.readFileSync(PUB + f); return { ok: true, status: 200, json: async () => JSON.parse(b), text: async () => b.toString() }; };
  w.scrollTo = () => {}; w.HTMLElement.prototype.scrollIntoView = function () {};
  w.localStorage.setItem('patente_dev', '1');
  const sc = w.document.createElement('script'); sc.textContent = SRC; w.document.body.appendChild(sc);
  for (let i = 0; i < 60 && !w.eval('questions.length'); i++) await wait(100);
  const q = w.eval('questions[0]'), st = q.statements[0];
  const build = () => w.buildFlagControl(q, st);
  let c = build();
  c.querySelector('.dev-flag-btn').click();
  const note = c.querySelector('.dev-flag-note');
  note.value = 'half-written comment'; note.dispatchEvent(new w.Event('input'));
  c.querySelector('.dev-flag-cat').value = 'question'; c.querySelector('.dev-flag-cat').dispatchEvent(new w.Event('change'));
  c = build();   // the card is rebuilt after a visit to another page
  ck(c.querySelector('.dev-flag-note').value === 'half-written comment', 'the draft comes back');
  ck(c.querySelector('.dev-flag-cat').value === 'question', 'with its category');
  ck(!c.querySelector('.dev-flag-form').classList.contains('hidden'), 'and the form is open');
  c.querySelector('.dev-flag-save').click();
  ck(w.eval('loadFlags()').some(f => String(f.number) === String(st.number) && f.note === 'half-written comment'), 'saving stores the flag');
  c = build();
  ck(c.querySelector('.dev-flag-form').classList.contains('hidden'), 'after saving, no draft reopens the form');
  c.querySelector('.dev-flag-btn').click();
  const n2 = c.querySelector('.dev-flag-note'); n2.value = 'edit then cancel'; n2.dispatchEvent(new w.Event('input'));
  c.querySelector('.dev-flag-cancel').click();
  c = build();
  ck(c.querySelector('.dev-flag-note').value === 'half-written comment', 'Cancel discards the draft and shows the saved note');
  // an old draft expires
  w.eval(`setFlagDraft(${st.number}, { cat: 'other', note: 'stale', t: Date.now() - 30*86400000 })`);
  c = build();
  ck(c.querySelector('.dev-flag-note').value !== 'stale', 'a draft older than two weeks is dropped');
  // A sent comment never shows on the card (20261010x, maintainer, 2026-10-04).
  w.eval(`setFlagDraft(${st.number}, null)`);
  w.eval(`saveFlags([{ number: ${st.number}, category: 'explanation', note: 'sent one', ts: Date.now() - 60000, sentAt: Date.now() - 1000 }])`);
  c = build();
  ck(/Flag issue|Segnala problema/.test(c.querySelector('.dev-flag-btn').textContent) && c.querySelector('.dev-flag-note').value === '' && !c.querySelector('.dev-flag-del'), 'a sent comment does not show on the card: Flag issue, empty form');
  c.querySelector('.dev-flag-btn').click(); c.querySelector('.dev-flag-note').value = 'a new comment'; c.querySelector('.dev-flag-save').click();
  const all = w.eval('loadFlags()');
  ck(all.length === 2 && all.some(f => f.note === 'sent one' && f.sentAt) && all.some(f => f.note === 'a new comment' && !f.sentAt), 'a new comment beside it keeps the sent record');
  c = build();
  ck(/Flagged|Segnalata/.test(c.querySelector('.dev-flag-btn').textContent) && c.querySelector('.dev-flag-note').value === 'a new comment', 'the card shows only the unsent one');
  c.querySelector('.dev-flag-btn').click(); c.querySelector('.dev-flag-del').click();
  ck(w.eval('loadFlags()').length === 1 && w.eval('loadFlags()')[0].note === 'sent one', 'Remove on the card takes the unsent comment and leaves the sent record');
  console.log(fail ? `${fail} FAILED, ${pass} passed` : `${pass}/${pass} passed`);
  process.exit(fail ? 1 : 0);
})();
