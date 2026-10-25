<?php
/**
 * Receives flagged-question reports from the app (reviewer mode) and appends them
 * to a file OUTSIDE the web root. The maintainer is emailed a summary when
 * 'notify_email' is set in secrets.php (see notify.php). Spam guards: app token, honeypot, size cap, per-IP rate limit.
 *
 * SETUP (edit the two CONFIG lines):
 *   1. $TOKEN must match APP_SUBMIT_TOKEN in app.js (this is NOT a secret — it is
 *      visible in the app — it just stops trivial bots).
 *   2. $STORE_DIR is where submissions are written. The default is one level above
 *      public_html, so it is not web-accessible and not inside the folder you sync.
 */

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

// ── CONFIG ───────────────────────────────────────────────────────────
$CFG = is_file(__DIR__ . '/secrets.php') ? (require __DIR__ . '/secrets.php') : [];
if (!is_array($CFG)) $CFG = [];
$TOKEN     = $CFG['submit_token'] ?? 'cc625673555839cf5e0d0643f59c0e42';  // = APP_SUBMIT_TOKEN in app.js (public)
$STORE_DIR = __DIR__ . '/../patente_flags';            // outside web root + outside the synced folder

// Trusted reviewers (code => display name) come from the private secrets.php so
// the codes never live in the (open-source) repo. Empty if secrets.php is absent.
$REVIEWERS = $CFG['reviewers'] ?? [];
$MAX_BYTES   = 65536;   // 64 KB body cap
$MAX_FLAGS   = 500;     // per submission
$RATE_MAX    = 30;      // submissions
$RATE_WINDOW = 600;     // per 10 minutes per IP
// ─────────────────────────────────────────────────────────────────────

function fail($code, $err) { http_response_code($code); echo json_encode(['ok' => false, 'error' => $err]); exit; }

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') fail(405, 'method');

$raw = file_get_contents('php://input', false, null, 0, $MAX_BYTES + 1);
if ($raw === false || strlen($raw) > $MAX_BYTES) fail(413, 'too_large');

$data = json_decode($raw, true);
if (!is_array($data)) fail(400, 'bad_json');

// Honeypot: the app always sends this empty; a bot that fills it is silently dropped.
if (!empty($data['website'])) { echo json_encode(['ok' => true]); exit; }

if (!hash_equals($TOKEN, (string)($data['token'] ?? ''))) fail(403, 'token');

$flags = $data['flags'] ?? null;
if (!is_array($flags) || count($flags) === 0) fail(400, 'no_flags');
if (count($flags) > $MAX_FLAGS) fail(413, 'too_many');

if (!is_dir($STORE_DIR)) @mkdir($STORE_DIR, 0700, true);
// Defense-in-depth: these folders sit beside the web root, so make sure the
// deny-all .htaccess exists on EVERY request, not only when the folder is
// first created (folders created by older versions may lack it).
if (!is_file($STORE_DIR . '/.htaccess')) {
  @file_put_contents($STORE_DIR . '/.htaccess',
    "<IfModule mod_authz_core.c>\n  Require all denied\n</IfModule>\n" .
    "<IfModule !mod_authz_core.c>\n  Order allow,deny\n  Deny from all\n</IfModule>\n");
}
if (!is_dir($STORE_DIR) || !is_writable($STORE_DIR)) fail(500, 'store');

// Per-IP rate limit (timestamps in a small file).
$ip     = $_SERVER['REMOTE_ADDR'] ?? '0';
$iphash = substr(hash('sha256', $ip), 0, 16);
$rlFile = $STORE_DIR . '/rl_' . $iphash . '.txt';
$now    = time();
$hits   = is_file($rlFile)
  ? array_filter(array_map('intval', explode("\n", trim((string)@file_get_contents($rlFile)))), fn($t) => $t > $now - $RATE_WINDOW)
  : [];
if (count($hits) >= $RATE_MAX) fail(429, 'rate');
$hits[] = $now;
@file_put_contents($rlFile, implode("\n", $hits), LOCK_EX);

// Opportunistic GC: rl_ files whose last write predates the rate window are
// dead (their timestamps no longer count), and mobile IPs rotate constantly,
// so without a sweep the folder grows one tiny file per IP forever.
if (random_int(1, 20) === 1) {
  foreach ((array)@glob($STORE_DIR . '/rl_*.txt') as $old) {
    $m = @filemtime($old);
    if ($m !== false && $m < $now - $RATE_WINDOW) @unlink($old);
  }
}

// Keep only the fields we expect, trimmed, so a bad payload can't bloat the file.
$clean = [];
foreach ($flags as $f) {
  if (!is_array($f)) continue;
  $clean[] = [
    'number'   => mb_substr((string)($f['number']   ?? ''), 0, 120),
    'category' => mb_substr((string)($f['category'] ?? ''), 0, 60),
    'answer'   => mb_substr((string)($f['answer']   ?? ''), 0, 10),
    'topic'    => mb_substr((string)($f['topic']    ?? ''), 0, 160),
    'italian'  => mb_substr((string)($f['italian']  ?? ''), 0, 400),
    'english'  => mb_substr((string)($f['english']  ?? ''), 0, 400),
    'note'     => mb_substr((string)($f['note']     ?? ''), 0, 800),
  ];
}

// Reviewer trust: a code present in $REVIEWERS is "trusted" and resolves to a
// name. An entry is either 'code' => 'Name' or, since 2026-09-24,
// 'code' => ['name' => 'Name', 'email' => 'x@y']. The email stays in
// secrets.php: it is never written into the submissions file, and the admin
// page looks it up by name when it draws a reply link.
$rcode    = trim((string)($data['reviewer'] ?? ''));
$trusted  = $rcode !== '' && isset($REVIEWERS[$rcode]);
$rentry   = $trusted ? $REVIEWERS[$rcode] : null;
$reviewer = $trusted ? (is_array($rentry) ? (string)($rentry['name'] ?? $rcode) : (string)$rentry)
                     : mb_substr($rcode, 0, 40);

// Instruction for whoever (or whatever) processes this file later. The review
// batches are handed to an AI assistant, which reads the record verbatim; this
// line tells it what a complete reply looks like, so the expectation travels
// with the data instead of being restated by hand each time.
$INSTRUCTIONS = 'When addressing this review batch: fix each flagged item, then '
  . 'reply comment by comment — quote or reference each flag number and describe '
  . 'exactly what changed for it (or say why no change was warranted). Keep '
  . 'Italian and English explanations equivalent in teaching content, and add '
  . 'vocabulary glosses for any term a B1 learner would not know. When a flag '
  . 'shows '
  . 'a reviewer was confused about a sign, term or concept, put the correction '
  . 'where the reader FIRST meets it in the topic review (the bullet that '
  . 'introduces it, with its picture), not only in the later rules section or '
  . 'in the question explanation. For flags in the "ambiguous" category, first '
  . 'try to DEFEAT the flag: attempt to justify the official answer from the '
  . 'statement\'s own words, the bank\'s definitions, and sibling statements on '
  . 'the same card. If a decisive argument exists, do not mark the question '
  . 'ambiguous; strengthen the explanation with that argument instead. Mark it '
  . '(warn/warn_it) only when a competent reader applying the words\' ordinary '
  . 'meaning could still justify the opposite answer. When rewriting a question '
  . 'explanation, it must teach the WHY drawn from the proofed topic review (the '
  . 'rule, mechanism, exception list, or trap word that decides the answer), '
  . 'never merely assert the conclusion or restate the statement as true/false. '
  . 'On cards that test membership (who may pass, who is banned, who may be '
  . 'overtaken), every explanation must repeat the list in both directions, allowed and banned, since those cards are memorization tasks. '
  . 'Flags in the "question" category are the reviewer asking the developer '
  . 'something: answer the question plainly in the reply, and change content '
  . 'only if the answer shows the content is wrong or unclear. '
  . 'A flag whose number starts with "vocab:", "gloss:" or "num:" is about a '
  . 'Reference entry (vocabulary.json, glossary.json or reference.json), not '
  . 'a statement; fix it in that file.';

$record = [
  'instructions' => $INSTRUCTIONS,
  'ts'       => gmdate('c'),
  'iphash'   => $iphash,
  'trusted'  => $trusted,
  'reviewer' => $reviewer,
  'version' => mb_substr((string)($data['version'] ?? ''), 0, 20),
  'note'    => mb_substr((string)($data['note'] ?? ''), 0, 1000),
  'flags'   => $clean,
];

$ok = @file_put_contents($STORE_DIR . '/flags.jsonl',
  json_encode($record, JSON_UNESCAPED_UNICODE) . "\n", FILE_APPEND | LOCK_EX);
if ($ok === false) fail(500, 'write');

// Email the maintainer (only if 'notify_email' is set in secrets.php). A
// trusted reviewer's address from secrets.php goes into Reply-To.
require_once __DIR__ . '/notify.php';
$rmail = ($trusted && is_array($rentry)) ? trim((string)($rentry['email'] ?? '')) : '';
$n     = count($clean);
$lines = [];
foreach (array_slice($clean, 0, 40) as $f) {
  $lines[] = '#' . $f['number'] . ' [' . $f['category'] . '] ' . $f['note'];
}
$body = ($reviewer !== '' ? $reviewer : 'An unnamed reviewer') . ($trusted ? '' : ' (untrusted code)')
      . " sent $n comment" . ($n === 1 ? '' : 's') . ".\n"
      . ($record['note'] !== '' ? "\nNote: " . $record['note'] . "\n" : '')
      . "\n" . implode("\n\n", $lines) . "\n"
      . ($n > 40 ? "\n(" . ($n - 40) . " more in the file)\n" : '')
      . "\nAll comments: " . (patente_admin_link($CFG, 'flags') ?: 'admin.php on the site') . "\n";
patente_notify($CFG, $STORE_DIR, "Patente B: $n reviewer comment" . ($n === 1 ? '' : 's') . ($reviewer !== '' ? " from $reviewer" : ''), $body, $rmail);

echo json_encode(['ok' => true, 'count' => count($clean)]);
