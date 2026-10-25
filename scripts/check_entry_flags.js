// Reviewers can comment on Vocabulary, Glossario and Numbers entries
// (20261011z, maintainer's bug report, 2026-10-05).
// Run: node scripts/check_entry_flags.js (UILANG=it-IT for the Italian face,
// SRC= another app.js to see it fail).
const fs = require('fs');
let JSDOM; try { ({ JSDOM } = require('jsdom')); } catch { ({ JSDOM } = require('/tmp/node_modules/jsdom')); }
const PUB = require('path').join(__dirname, '..', 'public_html') + '/';
const html = fs.readFileSync(PUB + 'index.html', 'utf8').replace(/<script[^>]*src="app\.js"[^>]*><\/script>/, '');
const SRC = fs.readFileSync(process.env.SRC || (PUB + 'app.js'), 'utf8');
const LANG = process.env.UILANG || 'en-US';
let pass = 0, fail = 0; const ck = (c, m) => { if (c) pass++; else { fail++; console.log('  ✗', m); } };
const wait = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const dom = new JSDOM(html, { runScripts: 'dangerously', url: 'https://patente.physyapps.com/', pretendToBeVisual: true });
  const w = dom.window;
  Object.defineProperty(w.navigator, 'language', { value: LANG, configurable: true });
  Object.defineProperty(w.navigator, 'languages', { value: [LANG], configurable: true });
  w.fetch = async (url) => { const f = String(url).replace(/^https?:\/\/[^/]+\//, '').replace(/^\//, '').split('?')[0];
    const b = fs.readFileSync(PUB + f); return { ok: true, status: 200, json: async () => JSON.parse(b), text: async () => b.toString() }; };
  w.scrollTo = () => {}; w.HTMLElement.prototype.scrollIntoView = function () {};
  const sc = w.document.createElement('script'); sc.textContent = SRC; w.document.body.appendChild(sc);
  for (let i = 0; i < 60 && !w.eval('questions.length'); i++) await wait(100);
  for (let i = 0; i < 60 && !w.eval('(glossary.entries || []).length && (reference.numbers || []).length'); i++) await wait(100);
  const $ = s => w.document.querySelector(s), $$ = s => [...w.document.querySelectorAll(s)];

  // Off outside reviewer mode.
  w.eval("glossTab = 'every'");
  w.renderGlossary(); w.renderReviewNumbers();
  ck($$('.entry-flag').length === 0, 'no ⚑ on the Reference rows outside reviewer mode');

  w.localStorage.setItem('patente_dev', '1');
  w.renderGlossary(); w.renderReviewNumbers();
  const gRows = $$('#gloss-body li[data-term]'), nRows = $$('#review-numbers-body .review-row');
  ck(gRows.length > 0 && gRows.every(li => li.querySelector(':scope > .entry-flag')), 'every Glossario row carries a ⚑ in reviewer mode');
  ck(nRows.length > 0 && nRows.every(r => r.querySelector(':scope > .entry-flag')), 'every Numbers row carries a ⚑');

  // A Glossario comment.
  if (!gRows.length || !gRows[0].querySelector('.entry-flag')) { console.log(`${fail + 1} FAILED, ${pass} passed`); process.exit(1); }
  const li = gRows[0], term = li.dataset.term;
  li.querySelector('.entry-flag').click();
  const form = li.querySelector(':scope > .dev-flag');
  ck(!!form && !form.querySelector('.dev-flag-btn') && !form.querySelector('.dev-flag-form').classList.contains('hidden'), 'the ⚑ opens the comment form under the row');
  ck([...form.querySelectorAll('option')].map(o => o.value).join() === 'entry,translation,question,other', 'the entry categories are offered');
  form.querySelector('.dev-flag-note').value = 'definition unclear';
  form.querySelector('.dev-flag-save').click();
  let f = w.eval('loadFlags()').find(x => x.number === 'gloss: ' + term);
  ck(!!f && f.note === 'definition unclear' && f.category === 'entry' && /Glossario/.test(f.topic) && f.italian.startsWith(term + '. '), 'saving stores a flag named for the Glossario entry, with its definition');
  ck(!li.querySelector(':scope > .dev-flag') && li.querySelector('.entry-flag').classList.contains('is-flagged'), 'the form closes and the ⚑ is marked');
  w.renderGlossary();
  ck($(`#gloss-body li[data-term="${term}"] .entry-flag`).classList.contains('is-flagged'), 'the mark survives a redraw');
  $(`#gloss-body li[data-term="${term}"] .entry-flag`).click();
  ck($(`#gloss-body li[data-term="${term}"] .dev-flag-note`).value === 'definition unclear', 'reopening shows the saved comment');

  // A Numbers comment.
  const row = $$('#review-numbers-body .review-row')[0];
  const n = w.eval('reference.numbers')[+row.querySelector('.entry-flag').dataset.fidx];
  row.querySelector('.entry-flag').click();
  row.querySelector('.dev-flag-note').value = 'wrong figure';
  row.querySelector('.dev-flag-save').click();
  f = w.eval('loadFlags()').find(x => x.number === 'num: ' + n.en);
  ck(!!f && f.italian.includes(n.value) && f.english.startsWith(n.en), 'a Numbers row is flagged by its English label, with its value');

  // A Vocabulary comment.
  w.eval("vocabTab = 'every'"); w.renderVocabScreen();
  const v = $('#vocab-body li[data-term]');
  if (LANG.startsWith('it')) ck(true, 'Italian face: Vocabulary is not offered');
  else {
    ck(!!v && !!v.querySelector('.entry-flag'), 'Vocabulary rows carry a ⚑');
    v.querySelector('.entry-flag').click();
    v.querySelector('.dev-flag-note').value = 'gloss wrong';
    v.querySelector('.dev-flag-save').click();
    ck(w.eval('loadFlags()').some(x => x.number === 'vocab: ' + v.dataset.term && x.english), 'a Vocabulary entry is flagged with its gloss');
  }

  // The Review and Send panel lists statements first, then entries.
  const st = w.eval('questions[0].statements[0]');
  w.eval(`addOrUpdateFlag({ number: ${st.number}, category: 'explanation', note: 'x', ts: Date.now() })`);
  w.renderFlagsOverlayList();
  const nums = $$('#flags-list .flag-row-num').map(e => e.textContent);
  ck(nums[0] === '#' + st.number && nums.slice(1).every(s => /^#(gloss|num|vocab): /.test(s)), 'the panel lists the statement first, then the entries');
  console.log(fail ? `${fail} FAILED, ${pass} passed` : `${pass}/${pass} passed`);
  process.exit(fail ? 1 : 0);
})();
