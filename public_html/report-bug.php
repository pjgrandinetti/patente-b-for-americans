<?php
/**
 * Receives app bug reports from the "Report a problem" form (open to all users)
 * and appends them to a file OUTSIDE the web root. The maintainer is emailed a
 * copy when 'notify_email' is set in secrets.php (see notify.php); nothing is
 * ever mailed to the submitter. A reply address is stored only when the user types one into
 * the form (optional since 2026-09-24); the developer replies by hand. Guards: app token, honeypot, size cap, per-IP rate limit.
 *
 * SETUP: $TOKEN must equal APP_SUBMIT_TOKEN in app.js (NOT a secret — visible in
 * the app — it just stops trivial bots). $STORE_DIR is one level above public_html,
 * so it is not web-accessible and not inside the synced folder.
 */

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

// ── CONFIG ───────────────────────────────────────────────────────────
$CFG = is_file(__DIR__ . '/secrets.php') ? (require __DIR__ . '/secrets.php') : [];
if (!is_array($CFG)) $CFG = [];
$TOKEN     = $CFG['submit_token'] ?? 'cc625673555839cf5e0d0643f59c0e42';  // = APP_SUBMIT_TOKEN in app.js (public)
$STORE_DIR = __DIR__ . '/../patente_bugs';            // outside web root + outside the synced folder
$REVIEWERS = $CFG['reviewers'] ?? [];
$MAX_BYTES   = 16384;   // 16 KB body cap
$RATE_MAX    = 20;      // reports
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

$report = trim((string)($data['report'] ?? ''));
if ($report === '') fail(400, 'empty');

if (!is_dir($STORE_DIR)) {
  @mkdir($STORE_DIR, 0700, true);
  @file_put_contents($STORE_DIR . '/.htaccess',
    "<IfModule mod_authz_core.c>\n  Require all denied\n</IfModule>\n" .
    "<IfModule !mod_authz_core.c>\n  Order allow,deny\n  Deny from all\n</IfModule>\n");
}
// Defense-in-depth: these folders sit beside the web root, so make sure the
// deny-all .htaccess exists on EVERY request, not only when the folder is
// first created (folders created by older versions may lack it).
if (!is_file($STORE_DIR . '/.htaccess')) {
  @file_put_contents($STORE_DIR . '/.htaccess',
    "<IfModule mod_authz_core.c>\n  Require all denied\n</IfModule>\n" .
    "<IfModule !mod_authz_core.c>\n  Order allow,deny\n  Deny from all\n</IfModule>\n");
}
if (!is_dir($STORE_DIR) || !is_writable($STORE_DIR)) fail(500, 'store');

// Per-IP rate limit (timestamps in a small file; IP is hashed, never stored raw).
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

// Trimmed context, so a bad payload can't bloat the file.
$ctx = is_array($data['context'] ?? null) ? $data['context'] : [];
$clean_ctx = [
  'version' => mb_substr((string)($ctx['version'] ?? ''), 0, 20),
  'level'   => mb_substr((string)($ctx['level']   ?? ''), 0, 20),
  'screen'  => mb_substr((string)($ctx['screen']  ?? ''), 0, 40),
  'lang'    => mb_substr((string)($ctx['lang']    ?? ''), 0, 8),
  'ua'      => mb_substr((string)($ctx['ua']      ?? ''), 0, 300),
];

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

// Optional reply address. Kept only if it is a plausible address; anything else
// is dropped silently rather than failing a report someone took time to write.
$email = trim((string)($data['email'] ?? ''));
if ($email !== '' && (strlen($email) > 254 || !filter_var($email, FILTER_VALIDATE_EMAIL))) $email = '';

$record = [
  'ts'       => gmdate('c'),
  'iphash'   => $iphash,
  'trusted'  => $trusted,
  'reviewer' => $reviewer,
  'email'    => $email,
  'report'   => mb_substr($report, 0, 4000),
  'context'  => $clean_ctx,
];

$ok = @file_put_contents($STORE_DIR . '/bugs.jsonl',
  json_encode($record, JSON_UNESCAPED_UNICODE) . "\n", FILE_APPEND | LOCK_EX);
if ($ok === false) fail(500, 'write');

// Email the maintainer (only if 'notify_email' is set in secrets.php).
require_once __DIR__ . '/notify.php';
$who  = $reviewer !== '' ? $reviewer . ($trusted ? '' : ' (untrusted code)') : 'a user';
$body = "New bug report from $who\n"
      . ($email !== '' ? "Reply address: $email (use Reply)\n" : "No reply address given.\n")
      . "\n" . $record['report'] . "\n\n"
      . 'Version ' . $clean_ctx['version'] . ', screen ' . $clean_ctx['screen']
      . ', level ' . $clean_ctx['level'] . ', language ' . $clean_ctx['lang'] . "\n"
      . $clean_ctx['ua'] . "\n\n"
      . "All reports: " . (patente_admin_link($CFG, 'bugs') ?: 'admin.php on the site') . "\n";
patente_notify($CFG, $STORE_DIR, 'Patente B: bug report' . ($email !== '' ? ' (reply requested)' : ''), $body, $email);

echo json_encode(['ok' => true]);
