/**
 * Service Worker — Patente B
 *
 * Strategy:
 *   - App shell & code (html / js / css / manifest) → NETWORK-FIRST:
 *     always fetch the latest when online, fall back to cache when offline, so
 *     UI/logic updates apply immediately without a manual version bump.
 *   - Large data files (questions / vocabulary / topic_reviews .json) →
 *     CACHE-FIRST on a URL stamped with the app version (`?v=20260916y`), in a
 *     cache that is not itself versioned. A hit is therefore always the copy
 *     this release shipped with, and a new release always fetches its own,
 *     so code and data can never disagree; the install step warms them.
 *   - Sign images (domandeb_images/) → CACHE-FIRST in a version-independent cache,
 *     and PRECACHED in full on install (~3.5 MB) so the app works fully offline,
 *     not just for images already viewed.
 */

const CACHE_VERSION = 'patente-netfirst-20261029c';
const BASE          = '';

// Small app shell — versioned cache, network-first so code/UI updates apply at once.
const SHELL_ASSETS  = [
  BASE + '/',
  BASE + '/index.html',
  BASE + '/app.js',
  BASE + '/style.css',
  BASE + '/manifest.json',
  BASE + '/manifest-it.json',
  BASE + '/abridged.json',
  BASE + '/image_aliases.json',
  BASE + '/review_anchors.json',
  BASE + '/reference.json',
  BASE + '/vocab_sets.json',
  BASE + '/grammar.json',
  BASE + '/glossary.json',
  BASE + '/favicon.ico',
  BASE + '/icons/icon.svg',
  BASE + '/review_media/green-wave.svg',
  BASE + '/review_media/disco-orario.svg',
  BASE + '/review_media/license-containment.svg',
  BASE + '/review_media/stopping-distance.svg',
  BASE + '/review_media/braking-distance-squared.svg',
  BASE + '/review_media/trailer-combination-mass.svg',
  BASE + '/review_media/license-points.svg',
  BASE + '/review_media/speed-limits-en.svg',
  BASE + '/review_media/speed-limits-it.svg',
];

// Large data files — kept in a SEPARATE cache, served cache-first, and asked
// for under a version-stamped URL so each release gets its own entry.
const DATA_CACHE = 'patente-data-v1';
// The data cache is deliberately version-independent, and each file is asked
// for under a URL that carries ITS OWN CONTENT HASH, `questions.json?v=3f2a…`,
// so the entry changes exactly when the file does. Two earlier schemes both
// cost something. An unversioned URL let a new APP_VERSION run against data
// cached several releases back (claims live inside topic_reviews.json, so
// stale notes silently dropped a statement's claim; reported 2026-09-13).
// Stamping APP_VERSION into the URL fixed that and made every release,
// including a one-line CSS change, re-download all three files on every
// device: one day of releases on 2026-09-23 showed questions.json fetched 34
// times by one person, 30 MB. The hash is stamped by
// scripts/stamp_data_hashes.py into BOTH this file and app.js (`DATA_HASH`),
// and validate_data.py fails when either is stale. Keep `dataUrl` here and in
// app.js in step.
const DATA_HASH = { 'questions.json': '28df19b7ab9d', 'vocabulary.json': 'a2e60b1cc223', 'topic_reviews.json': '10d27cfefd4e' };
const dataUrl = name => `${BASE}/${name}?v=${DATA_HASH[name]}`;
const dataHashFor = pathname => DATA_HASH[pathname.slice(pathname.lastIndexOf('/') + 1)];
// True only if the response body is complete, valid JSON. A truncated file
// still arrives with 200 OK, so status alone proves nothing, and under
// cache-first an unusable copy would be served for the whole release.
async function isWholeJson(resp) {
  try { await resp.clone().json(); return true; } catch { return false; }
}
const DATA_FILES = /\/(questions|vocabulary|topic_reviews)\.json$/;

// Sign images — separate, version-independent cache, fully precached on install.
const IMG_CACHE = 'patente-img-v1';
// Images whose CONTENT changed under an existing file name. The image cache is
// keyed by path and never expires, so an edited file (labels added to a
// figure, a redrawn sign) would otherwise stay stale on every installed
// device forever. Listing the path here makes the installing worker drop the
// cached copy and fetch the new one. Add to this list whenever an existing
// image file is replaced; entries can be pruned after a few releases.
const IMG_REFRESH = [
  BASE + '/domandeb_images/4256.svg',          // 20260908k: A, B, C labels and white plate
  BASE + '/domandeb_images/4244_21010.svg',    // 20260908k: same figure
  BASE + '/domandeb_images/4249.svg',          // 20260908k: A, B labels restored
  BASE + '/domandeb_images/4258.svg',          // 20260908k: same figure
  BASE + '/domandeb_images/4186.svg',          // 20260908k: hidden tracing bitmaps removed (8 MB -> 40 KB)
  BASE + '/domandeb_images/4187.svg',          // 20260908k: hidden tracing bitmaps removed (8 MB -> 40 KB)
  BASE + '/domandeb_images/4188.svg',          // 20260908k: hidden tracing bitmaps removed (8 MB -> 40 KB)
  BASE + '/domandeb_images/4192.svg',          // 20260908k: hidden tracing bitmaps removed (8 MB -> 40 KB)
];

// Files that should always be revalidated from the network when online
const NETWORK_FIRST = /\.(?:html|js|css|json)$/;

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    // Precache the shell into the versioned cache (bypass HTTP cache for freshness).
    // Best-effort PER ASSET: cache.addAll() rejects the whole batch if ANY single
    // request fails (e.g. one file 404s after a partial upload), which aborts the
    // install. An aborted install never reaches the "installed" state, so the app's
    // "Downloading update…" status hangs forever with no way out. Fetching each
    // asset independently means one missing file degrades gracefully instead of
    // bricking the update; runtime network-first/cache-first fills any gap later.
    const shell = await caches.open(CACHE_VERSION);
    await Promise.all(SHELL_ASSETS.map(async u => {
      try {
        const r = await fetch(new Request(u, { cache: 'no-cache' }));
        const len = r && r.headers.get('content-length');
        if (r && r.ok && !(len !== null && Number(len) === 0)) await shell.put(u, r);
      } catch { /* offline or missing → handled at runtime */ }
    }));

    // Refresh ALL data files on a new-version install so a content update (new
    // reviews / questions / vocabulary) is already fresh in the cache by the time
    // the user taps "Restart now" — not one launch behind. On failure (offline)
    // keep whatever copy we already have, so we never end up with nothing; SWR
    // will still refresh it later. Cost: ~2.6 MB re-download per app update, which
    // the version bump implies anyway. (questions.json is refreshed first so the
    // image precache below reads the new image list.)
    // A file already cached under its hash is the same bytes, so it is left
    // alone: the page, still run by the old worker, has usually fetched a
    // changed file already, and refetching it here was the second of the two
    // downloads per release the log showed.
    const data = await caches.open(DATA_CACHE);
    for (const u of [dataUrl('questions.json'), dataUrl('vocabulary.json'), dataUrl('topic_reviews.json')]) {
      try {
        if (await data.match(u)) continue;
        const resp = await fetch(new Request(u, { cache: 'no-cache' }));
        if (resp && resp.ok && await isWholeJson(resp)) await data.put(u, resp);
      } catch { /* offline → keep the existing copy; the fetch handler retries */ }
    }

    // Precache every sign image (~3.5 MB) so the app works offline even for cards
    // not yet opened. The list comes from questions.json (kept in sync); images
    // already cached are skipped, so a shell update never re-downloads them.
    try {
      const imgCache = await caches.open(IMG_CACHE);
      for (const p of IMG_REFRESH) { try { await imgCache.delete(p); } catch { /* ignore */ } }
      const qresp = await data.match(dataUrl('questions.json'));
      if (qresp) {
        const questions = await qresp.clone().json();
        const paths = [...new Set(questions.filter(q => q.image).map(q => BASE + '/' + q.image))];
        // Fetch every current image not already cached, keyed by PATH (not count).
        // Each image is looked up individually and skipped if present, so a
        // shell-only update fetches nothing, while an image swap (e.g. .jpeg → .svg)
        // fetches just the new files. A count-based check was unreliable: the old
        // files linger in this version-independent cache, so the count still
        // matched and the new files were silently never precached.
        const CONCURRENCY = 12;
        for (let i = 0; i < paths.length; i += CONCURRENCY) {
          await Promise.all(paths.slice(i, i + CONCURRENCY).map(async p => {
            if (await imgCache.match(p)) return;
            try { const r = await fetch(p, { cache: 'reload' }); if (r && r.ok) await imgCache.put(p, r); }
            catch { /* offline → cache-first will fill it on demand later */ }
          }));
        }
        // Evict images no longer referenced (e.g. the .jpeg a card no longer uses
        // after being switched to .svg), so the cache doesn't grow without bound
        // and a stale file can't mask a genuinely missing one.
        const wanted = new Set(paths);
        for (const request of await imgCache.keys()) {
          const path = new URL(request.url).pathname;
          if (path.includes('/domandeb_images/') && !wanted.has(path)) {
            await imgCache.delete(request);
          }
        }
      }
    } catch { /* best effort */ }
  })());
  // Do NOT skipWaiting here. The new worker stays in "waiting" so the app can
  // prompt the user to restart, then activate on demand (see message handler).
});

// Activate immediately when the page asks us to (user clicked "Restart now")
self.addEventListener('message', event => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    // Drop old shell caches, but KEEP the data and image caches.
    const keys = await caches.keys();
    await Promise.all(keys
      .filter(k => k !== CACHE_VERSION && k !== DATA_CACHE && k !== IMG_CACHE)
      .map(k => caches.delete(k)));
    // Inside the data cache, drop the entries stamped with an older version,
    // but only once THIS version's copy of that file is actually there: while
    // an update installs offline the old copy is the only data the app has, and
    // deleting it would leave the learner with none. Without this prune the
    // cache would grow by ~6 MB per release.
    const data = await caches.open(DATA_CACHE);
    const reqs = await data.keys();
    const isCurrent = u => u.searchParams.get('v') === dataHashFor(u.pathname);
    const fresh = new Set(reqs.map(r => new URL(r.url)).filter(isCurrent).map(u => u.pathname));
    await Promise.all(reqs.filter(r => {
      const u = new URL(r.url);
      return !isCurrent(u) && fresh.has(u.pathname);
    }).map(r => data.delete(r)));
  })());
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return; // POST (share target) handled below

  const url = new URL(req.url);

  // Sign images — cache-first against the version-independent image cache.
  if (url.pathname.includes('/domandeb_images/')) {
    event.respondWith(
      caches.open(IMG_CACHE).then(cache =>
        cache.match(req).then(cached =>
          cached || fetch(req).then(resp => {
            if (resp && resp.ok) cache.put(req, resp.clone());
            return resp;
          })
        )
      )
    );
    return;
  }

  // Large data files — cache-first on a URL that carries the version, so a hit
  // is by definition the copy this release shipped with and needs no
  // revalidation. (It used to be stale-while-revalidate on an unversioned URL,
  // which is how a new release could read old notes for a whole launch.) A miss
  // goes to the network; if that fails we are offline on a fresh update, so
  // fall back to any copy of the same file left by an earlier version, which is
  // better than no data at all.
  if (DATA_FILES.test(url.pathname)) {
    event.respondWith((async () => {
      const cache = await caches.open(DATA_CACHE);
      const hit = await cache.match(req);
      if (hit) return hit;
      try {
        const resp = await fetch(req, { cache: 'no-cache' });
        if (!resp || !resp.ok) return resp;
        // ONE body at a time. This used to read a clone to prove the JSON
        // parses, clone AGAIN for the cache, and hand the original to the page:
        // three live copies of a 5.5 MB file, measured at 11.9 MB of heap, in a
        // service worker, on a phone. Two real visitors on 2026-09-22 fetched
        // questions.json TEN times each, about 10 MB, on their first load.
        // `cache.put` consumes the response outright, and the page is then
        // served the copy read back out of the cache, so the peak is one body
        // rather than three.
        //
        // Nothing is validated here any more, and that is deliberate rather
        // than a regression: `loadDataFile` in app.js already parses what it
        // gets, deletes the cache entry and refetches when it will not parse,
        // which is the same un-sticking this check was written to provide. Two
        // layers were doing one job and the expensive one sat on the device
        // with the least memory. The INSTALL step keeps its own `isWholeJson`,
        // where no copy has to be handed on and the check is nearly free.
        await cache.put(req, resp);
        return (await cache.match(req)) || Response.error();
      } catch {
        for (const k of await cache.keys()) {
          if (new URL(k.url).pathname === url.pathname) {
            const old = await cache.match(k);
            if (old) return old;
          }
        }
        throw new Error('offline and no cached copy of ' + url.pathname);
      }
    })());
    return;
  }

  // App shell, code, and page navigations — network-first.
  // `cache: 'no-cache'` always asks the server, which is what the old
  // `'reload'` was for (an asset stored with a long max-age before the
  // no-cache headers were fixed kept being served stale), but it sends the
  // conditional request, so an unchanged file comes back as a bodiless 304
  // and the copy in the browser's HTTP cache is used. With `'reload'` the
  // conditional request was never made: the log for 2026-09-23 showed app.js
  // answered 200 on all fifty launches, 10.7 MB for one file, while .htaccess
  // had been written expecting "cheap 304s via ETag".
  if (req.mode === 'navigate' || NETWORK_FIRST.test(url.pathname)) {
    event.respondWith(
      fetch(req, { cache: 'no-cache' })
        .then(async resp => {
          // Only a GOOD response may be served or cached. A 404 or a 5xx (a
          // half-finished upload, a server hiccup) used to be returned to the
          // page AND written into the cache, which is how a blank screen can
          // survive a reload: the browser renders an error body, or an empty
          // one, with no way back. Fall back to the last known-good copy.
          // A file being uploaded is served as ZERO BYTES with 200 OK, which
          // passes an `ok` check and renders as a blank page. Treat an empty
          // shell/page response as a failure too.
          const len = resp && resp.headers.get('content-length');
          const empty = len !== null && len !== undefined && Number(len) === 0;
          if (!resp || !resp.ok || empty) {
            const cached = await caches.match(req) || await caches.match(BASE + '/');
            if (cached) return cached;
            return resp;                      // nothing cached: show the real error
          }
          const clone = resp.clone();
          caches.open(CACHE_VERSION).then(c => c.put(req, clone));
          return resp;
        })
        .catch(async () =>
          (await caches.match(req)) || (await caches.match(BASE + '/')) ||
          new Response('<!doctype html><meta charset=utf-8><title>Offline</title>' +
            '<body style="font:16px system-ui;padding:2rem"><h1>Offline</h1>' +
            '<p>The app could not be reached and nothing is cached yet.</p>' +
            '<button onclick="location.reload()">Try again</button>',
            { headers: { 'Content-Type': 'text/html; charset=utf-8' } })
        )
    );
    return;
  }

  // Anything else — cache-first, then network
  event.respondWith(
    caches.match(req).then(cached => cached || fetch(req))
  );
});

// Handle share_target file posts (iOS/Android PWA share sheet).
// Scope to POSTs aimed at the share-target action ('/') only, so other POSTs
// (e.g. submit-flags.php) pass straight through to the network.
self.addEventListener('fetch', event => {
  if (event.request.method !== 'POST') return;
  const p = new URL(event.request.url).pathname;
  if (p !== '/' && p !== BASE + '/') return;
  event.respondWith(
    (async () => {
      const formData = await event.request.formData();
      const file     = formData.get('file');
      const client   = await self.clients.get(event.clientId)
        ?? (await self.clients.matchAll())[0];
      if (client && file) {
        const text = await file.text();
        client.postMessage({ type: 'IMPORT_PROGRESS', payload: text });
      }
      return Response.redirect(BASE + '/', 303);
    })()
  );
});
