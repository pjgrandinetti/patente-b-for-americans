// Reviewers can comment on the licensing How-to and the driving test page
// (20261030u, maintainer's bug report, 2026-10-30).
// Run: node scripts/check_prose_flags.js (UILANG=it-IT for the Italian face,
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
  w.Element.prototype.scrollTo = function () {};
  const sc = w.document.createElement('script'); sc.textContent = SRC; w.document.body.appendChild(sc);
  for (let i = 0; i < 60 && !w.eval('questions.length'); i++) await wait(100);
  const $ = s => w.document.querySelector(s), $$ = s => [...w.document.querySelectorAll(s)];
  const box = $('[data-i18n-html="next.body"]');

  ck(box.querySelectorAll('.entry-flag').length === 0, 'no ⚑ in the How-to outside reviewer mode');
  w.eval('openDrivingTest()');
  ck($$('#review-body .entry-flag').length === 0, 'no ⚑ on the driving test page outside reviewer mode');

  w.localStorage.setItem('patente_dev', '1');
  w.applyI18n();
  const steps = [...box.querySelectorAll('.route-pane > ol > li')];
  ck(steps.length === 18 && steps.every(li => li.querySelector(':scope > .entry-flag')), 'every step of both routes carries a ⚑');
  ck([...box.querySelectorAll(':scope > p')].every(p => p.querySelector(':scope > .entry-flag')), 'every shared paragraph carries a ⚑');
  ck(box.querySelectorAll(':scope li li .entry-flag').length === 0, 'no ⚑ on a nested list item');
  w.applyRouteTab();
  ck(steps.every(li => li.querySelectorAll(':scope > .entry-flag').length === 1), 'repainting the tabs adds no second ⚑');

  const li = steps[3];
  li.querySelector('.entry-flag').click();
  const form = li.querySelector(':scope > .dev-flag');
  ck(!!form, 'the ⚑ opens the comment form under the step');
  ck([...form.querySelectorAll('option')].map(o => o.value).join() === 'text,translation,question,other', 'the passage categories are offered');
  form.querySelector('.dev-flag-note').value = 'out of date';
  form.querySelector('.dev-flag-save').click();
  let f = w.eval('loadFlags()').find(x => /^howto: school step 4, /.test(x.number));
  const it = LANG.startsWith('it');
  ck(!!f && f.note === 'out of date' && /How-to/.test(f.topic) && (it ? f.italian : f.english).length > 40 && !/⚑/.test(it ? f.italian : f.english),
     'saving stores a flag named for the step, with its text in the language shown');
  ck(li.querySelector('.entry-flag').classList.contains('is-flagged') && !li.querySelector(':scope > .dev-flag'), 'the form closes and the ⚑ is marked');

  w.eval('openDrivingTest()');
  const blocks = $$('#review-body p, #review-body li').filter(el => !el.closest('li') || el.closest('li') === el);
  ck(blocks.length > 10 && blocks.every(el => el.querySelector(':scope > .entry-flag')), 'every paragraph and bullet of the driving test page carries a ⚑');
  const b = blocks[2];
  b.querySelector('.entry-flag').click();
  b.querySelector('.dev-flag-note').value = 'check this';
  b.querySelector('.dev-flag-save').click();
  f = w.eval('loadFlags()').find(x => /^drive: /.test(x.number));
  ck(!!f && f.topic === 'Driving test page' && (f.english || f.italian).length > 20 && !/\bIT\b|\bEN\b/.test((f.english || f.italian).slice(-3)),
     'a driving test passage is flagged by its section, with its text and no pill label');

  console.log(fail ? `${fail} FAILED, ${pass} passed` : `✓ ${pass} checks passed`);
  process.exit(fail ? 1 : 0);
})();
