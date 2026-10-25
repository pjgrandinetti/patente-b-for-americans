// Reviewer flags across two devices: nothing is lost to a Send on another
// device, nothing sent goes out twice, and a sent flag is KEPT as a record
// (since 20260930t; before that a Send deleted it). Run: node scripts/check_flags_sync.js
// (SRC=path/to/app.js to test another build). See CLAUDE.md, reviewer flags.
// Two devices, A and B, each a jsdom window running the real app.js. Sync is
// modelled by handing one device's bundle to the other's mergeDeviceState,
// which is the function the real sync and import both call.
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
const nums = w => w.eval('loadFlags()').map(f => Number(f.number)).sort();
const unsent = w => w.eval('unsentFlags()').map(f => Number(f.number)).sort();
const sentN = w => w.eval('loadFlags().filter(flagSent)').map(f => Number(f.number)).sort();
const sync = (from, to) => to.mergeDeviceState(JSON.parse(JSON.stringify(from.buildProgressBundle())));
(async () => {
  const A = boot(), B = boot();
  for (let i = 0; i < 60 && !(A.eval('questions.length') && B.eval('questions.length')); i++) await wait(100);
  ck(A.eval('questions.length') > 0 && B.eval('questions.length') > 0, 'both devices booted');

  // 1. Saving a flag marks the state dirty, so sync will upload it.
  A.eval('_syncDirty = false'); flag(A, 1001, Date.now() - 50000);
  ck(A.eval('_syncDirty') === true, 'saving a flag marks sync dirty');

  // 2. THE REPORTED LOSS. B writes a flag that has not reached A. A sends.
  flag(B, 2002, Date.now() - 40000);            // written on B BEFORE A's send
  await A.submitFlags();
  ck(JSON.stringify(A.__posted[0]) === '[1001]', 'A sent only what it had');
  ck(unsent(A).length === 0, 'nothing is left to send on A');
  ck(sentN(A).includes(1001), 'the sent flag is KEPT on A, marked sent');
  sync(A, B);                                   // B pulls A's state
  ck(nums(B).includes(2002), "B's unsent flag SURVIVES A's send");
  sync(B, A);
  ck(nums(A).includes(2002), "and reaches A on the next sync");
  ck(!unsent(A).includes(1001) && !unsent(B).includes(1001), 'the sent flag is not queued to send again on either device');
  ck(sentN(B).includes(1001), 'and B shows it as sent');

  // 3. A flag saved WHILE the send is in flight survives it.
  let open; A.__postGate = new Promise(r => { open = r; });
  const sending = A.submitFlags();
  await wait(10);
  flag(A, 3003, Date.now());
  open(); await sending; A.__postGate = null;
  ck(nums(A).includes(3003), 'a flag saved during the send survives it');
  ck(sentN(A).includes(2002) && !unsent(A).includes(2002), 'the flag that was sent is marked sent');
  ck(unsent(A).includes(3003), 'and the one saved during the send is still waiting');

  // 4. A deleted flag is not resurrected by a device that still has it.
  flag(A, 4004, Date.now()); sync(A, B);
  ck(nums(B).includes(4004), 'B has 4004');
  A.eval(`retireFlags(loadFlags().filter(f => String(f.number) === '4004'))`);
  sync(B, A);
  ck(!nums(A).includes(4004), 'a deleted flag is not resurrected by a sync');
  sync(A, B);
  ck(!nums(B).includes(4004), 'and the deletion reaches the other device');

  // 5. Editing a sent flag makes a NEW comment that is not treated as sent.
  flag(A, 5005, 1000); await A.submitFlags();
  flag(A, 5005, 2000);
  ck(nums(A).includes(5005), 'a re-flag of a sent statement is kept');
  ck(unsent(A).includes(5005), 'and an edit puts it back among the unsent');

  // 7. Send again, and clearing the Sent list.
  await A.submitFlags();
  ck(!unsent(A).length, 'everything on A is sent');
  const posts = A.__posted.length;
  await A.submitFlags();
  ck(A.__posted.length === posts, 'a Send with nothing unsent posts nothing');
  A.eval(`(() => { const a = loadFlags(); const f = a.find(x => String(x.number) === '5005'); f.ts = Date.now(); saveFlags(a); })()`);
  await A.submitFlags();
  ck(JSON.stringify(A.__posted[A.__posted.length - 1]) === '[5005]', 'Send again posts only that flag');
  A.eval('retireFlags(loadFlags().filter(flagSent))');
  ck(nums(A).length === 0, 'Delete all sent empties the list');
  sync(A, B);
  ck(!nums(B).some(n => [1001, 2002, 3003, 5005].includes(n)), 'and the deletion reaches the other device');

  // 6. Legacy: an incoming old-style stamp is still honoured.
  const before = nums(B).length;
  B.mergeDeviceState({ flags: [], flagsClearedAt: 1 });
  ck(nums(B).length === before, 'a tiny legacy stamp removes nothing new');

  // 7. The overlay folds the SENT flags into a closed disclosure (20261003p),
  // and an open box stays open across a redraw within the session.
  flag(A, 6006, Date.now() - 1000); await A.submitFlags();
  flag(A, 7007, Date.now());
  A.eval('renderFlagsOverlayList()');
  const box = () => A.document.querySelector('#flags-list details.flags-sent');
  ck(box() && !box().open, 'sent flags sit in a CLOSED disclosure');
  ck(box() && box().querySelectorAll('.flag-row').length === sentN(A).length, 'every sent flag is inside it');
  ck(!A.document.querySelector('#flags-list > .flag-row-sent'), 'no sent row outside it');
  ck(A.document.querySelector('#flags-list > .flag-row'), 'unsent rows stay outside, visible');
  box().open = true; box().dispatchEvent(new A.Event('toggle'));
  A.eval('renderFlagsOverlayList()');
  ck(box() && box().open, 'an opened box stays open after a redraw');

  // A sent record and a new comment on the same statement (20261010x).
  {
    const n = 8008;
    flag(A, n, Date.now() - 5000); await A.submitFlags();
    sync(A, B);
    ck(B.eval(`loadFlags().filter(f => f.number == ${n} && flagSent(f)).length`) === 1, 'B receives the sent record');
    flag(B, n, Date.now());
    ck(B.eval(`loadFlags().filter(f => f.number == ${n}).length`) === 2 && B.eval(`flagFor(${n})`).note === 'n' + n && !B.eval(`flagSent(flagFor(${n}))`), 'a new comment on B sits beside the sent record');
    sync(B, A); sync(A, B);
    ck(A.eval(`loadFlags().filter(f => f.number == ${n}).length`) === 2 && B.eval(`loadFlags().filter(f => f.number == ${n}).length`) === 2, 'both devices keep both after syncing either way');
    B.eval(`addOrUpdateFlag(Object.assign({}, flagFor(${n}), { note: 'edited', ts: Date.now() + 10 }))`);
    sync(B, A);
    ck(A.eval(`loadFlags().filter(f => f.number == ${n} && !flagSent(f)).length`) === 1 && A.eval(`flagFor(${n})`).note === 'edited', 'an edit replaces the older unsent text, and only one unsent comment remains');
    A.eval('renderFlagsOverlayList()');
    const sentRow = A.document.querySelector(`#flags-list .flag-row-sent[data-number="${n}"]`);
    ck(sentRow && sentRow.querySelector('.flag-row-note').readOnly && sentRow.querySelector('.flag-row-cat').disabled && !sentRow.querySelector('.flag-row-resend'), 'the sent record is read-only, with no Send again while a newer comment is waiting');
    const live = A.document.querySelector(`#flags-list .flag-row:not(.flag-row-sent)[data-number="${n}"]`);
    const ta = live.querySelector('.flag-row-note');
    ta.value = 'typed one'; ta.dispatchEvent(new A.Event('input'));
    ta.value = 'typed two'; ta.dispatchEvent(new A.Event('input'));
    ck(A.eval(`flagFor(${n})`).note === 'typed two' && A.eval(`loadFlags().filter(f => f.number == ${n}).length`) === 2, 'typing in the unsent row edits that row only, keystroke after keystroke');
  }

  console.log(`\n${pass}/${pass + fail} passed`);
  process.exit(fail ? 1 : 0);
})();
