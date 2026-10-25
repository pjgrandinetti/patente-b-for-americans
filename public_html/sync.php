<?php
/**
 * End-to-end encrypted progress sync.
 *
 * The app encrypts the user's progress ON THE DEVICE with a key derived from a
 * sync code only the user holds, then stores the ciphertext here keyed by a hash
 * of that code (the "bucket"). This server only ever sees:
 *   - bucket: a SHA-256 hex hash of the code (preimage-resistant; never the code)
 *   - blob:   an opaque encrypted string it cannot read
 * No account, email, or personal data is involved, and we cannot decrypt anything.
 *
 *   POST {token, bucket, blob}  -> store/replace the blob for that bucket
 *   GET  ?token=..&bucket=..    -> return the stored blob (or 404)
 *
 * SETUP: $TOKEN must equal APP_SUBMIT_TOKEN in app.js (NOT a secret — it is
 * visible in the app — it just stops trivial bots). $STORE_DIR is one level above
 * public_html, so it is not web-accessible and not inside the synced folder.
 */

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

// ── CONFIG ───────────────────────────────────────────────────────────
$CFG = is_file(__DIR__ . '/secrets.php') ? (require __DIR__ . '/secrets.php') : [];
if (!is_array($CFG)) $CFG = [];
$TOKEN     = $CFG['submit_token'] ?? 'cc625673555839cf5e0d0643f59c0e42';  // = APP_SUBMIT_TOKEN in app.js (public)
$STORE_DIR = __DIR__ . '/../patente_sync';            // outside web root + outside the synced folder
$MAX_BYTES   = 4194304;  // 4 MB body cap (encrypted+base64 progress; generous)
$RATE_MAX    = 120;      // requests
$RATE_WINDOW = 600;      // per 10 minutes per IP
// ─────────────────────────────────────────────────────────────────────

function fail($code, $err) { http_response_code($code); echo json_encode(['ok' => false, 'error' => $err]); exit; }

$method = $_SERVER['REQUEST_METHOD'] ?? '';
if ($method !== 'POST' && $method !== 'GET') fail(405, 'method');

// Token gate (both verbs). hash_equals avoids timing leaks.
$token = $method === 'POST'
  ? null                                   // read from JSON body below
  : (string)($_GET['token'] ?? '');
if ($method === 'GET' && !hash_equals($TOKEN, $token)) fail(403, 'token');

// Bucket must be exactly a SHA-256 hex string — this also blocks path traversal,
// since only [a-f0-9] can ever reach the filename.
function valid_bucket($b) { return is_string($b) && preg_match('/^[a-f0-9]{64}$/', $b) === 1; }

// Ensure the store exists and is locked down (defense-in-depth deny file).
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

// Opportunistic garbage collection of stale rate-limit files. Every rl_ file
// whose last write predates the rate window is dead (its timestamps can no
// longer count against any limit), so on roughly 1 request in 20 we sweep them.
// This keeps the store at a handful of files with no cron job; mobile IPs
// rotate constantly, so without it the folder grows one tiny file per IP
// forever. Never touches the *.json sync buckets.
if (random_int(1, 20) === 1) {
  foreach ((array)@glob($STORE_DIR . '/rl_*.txt') as $old) {
    $m = @filemtime($old);
    if ($m !== false && $m < $now - $RATE_WINDOW) @unlink($old);
  }
}

// ── GET: download a bucket ────────────────────────────────────────────
// Conditional: the stored blob carries an `etag` (a hash of the ciphertext,
// written by the POST below). A client that already holds that exact blob sends
// it back as If-None-Match and gets a bodiless 304. This matters because the
// blob is the WHOLE progress bundle, a few hundred kilobytes, and the client
// syncs every few minutes while someone studies: without this, a device spends
// its entire session re-downloading a copy of what it just uploaded. Measured
// on one session, 2026-09-21: 126 pulls, 32.4 MB, every one of them redundant.
if ($method === 'GET') {
  $bucket = (string)($_GET['bucket'] ?? '');
  if (!valid_bucket($bucket)) fail(400, 'bad_bucket');
  $file = $STORE_DIR . '/' . $bucket . '.json';
  if (!is_file($file)) fail(404, 'not_found');
  $stored = json_decode((string)@file_get_contents($file), true);
  if (!is_array($stored)) fail(500, 'corrupt');
  $storedBlob = (string)($stored['blob'] ?? '');
  // Buckets written before this field existed are hashed on read, so an old
  // file answers conditionally too rather than forcing one last full pull.
  $etag = (string)($stored['etag'] ?? '');
  if ($etag === '') $etag = substr(hash('sha256', $storedBlob), 0, 32);
  header('ETag: "' . $etag . '"');
  $inm = trim((string)($_SERVER['HTTP_IF_NONE_MATCH'] ?? ''));
  if ($inm !== '' && trim(preg_replace('/^W\//', '', $inm), '"') === $etag) {
    http_response_code(304);
    exit;                                   // 304 carries no body, by definition
  }
  echo json_encode([
    'ok'        => true,
    'blob'      => $storedBlob,
    'updatedAt' => $stored['updatedAt'] ?? null,
    'etag'      => $etag,                   // also in the body, so a proxy that
  ]);                                       // strips headers cannot break this
  exit;
}

// ── POST: store/replace a bucket ──────────────────────────────────────
$raw = file_get_contents('php://input', false, null, 0, $MAX_BYTES + 1);
if ($raw === false || strlen($raw) > $MAX_BYTES) fail(413, 'too_large');

$data = json_decode($raw, true);
if (!is_array($data)) fail(400, 'bad_json');

// Honeypot: the app always sends this empty; a bot that fills it is silently dropped.
if (!empty($data['website'])) { echo json_encode(['ok' => true]); exit; }

if (!hash_equals($TOKEN, (string)($data['token'] ?? ''))) fail(403, 'token');

$bucket = (string)($data['bucket'] ?? '');
if (!valid_bucket($bucket)) fail(400, 'bad_bucket');

$blob = $data['blob'] ?? null;
if (!is_string($blob) || $blob === '') fail(400, 'no_blob');

$updatedAt = gmdate('c');
// The etag is a hash of the ciphertext, so it changes if and only if the stored
// blob changes. It is written here rather than computed on every GET because a
// push happens once per sync cycle and a pull happens on every one of them.
$etag = substr(hash('sha256', $blob), 0, 32);
$payload = json_encode([
  'v'         => 1,
  'blob'      => $blob,           // opaque ciphertext envelope produced on the device
  'updatedAt' => $updatedAt,
  'etag'      => $etag,
], JSON_UNESCAPED_UNICODE);

// Atomic write: temp file + rename, so a concurrent GET never sees a half-written file.
$file = $STORE_DIR . '/' . $bucket . '.json';
$tmp  = $file . '.' . bin2hex(random_bytes(4)) . '.tmp';
if (@file_put_contents($tmp, $payload, LOCK_EX) === false) fail(500, 'write');
if (!@rename($tmp, $file)) { @unlink($tmp); fail(500, 'write'); }

// Activity record for the admin page (2026-09-27): when this bucket was first
// written, how many uploads it has made, and the distinct UTC days on which it
// uploaded (the last 120). Dates and counts only, beside the blob in a small
// sidecar, so the admin page never has to open the ciphertext. A failure here
// is ignored: it must never cost the user a sync.
$metaFile = $STORE_DIR . '/' . $bucket . '.meta.json';
$meta = is_file($metaFile) ? json_decode((string)@file_get_contents($metaFile), true) : null;
if (!is_array($meta)) $meta = ['first' => $updatedAt, 'pushes' => 0, 'days' => []];
$meta['pushes'] = (int)($meta['pushes'] ?? 0) + 1;
$day = gmdate('Y-m-d');
$days = array_values(array_filter((array)($meta['days'] ?? []), 'is_string'));
if (!in_array($day, $days, true)) $days[] = $day;
$meta['days'] = array_slice($days, -120);
$meta['last'] = $updatedAt;
@file_put_contents($metaFile, json_encode($meta), LOCK_EX);

// Returning the etag is what makes the scheme pay: the pushing device stores it
// and its OWN next pull is a 304. Without this the client would know the remote
// had changed (it had, to our copy) and would download it back in full.
header('ETag: "' . $etag . '"');
echo json_encode(['ok' => true, 'updatedAt' => $updatedAt, 'etag' => $etag]);
