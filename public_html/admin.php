<?php
/**
 * Unified private admin page: sync statistics, flagged questions, bug reports.
 * Reach it at:  https://patente.physyapps.com/admin.php?key=YOUR_SECRET
 *
 * Replaces the three separate pages (sync-admin, flags-admin, bugs-admin),
 * which remain functional with their own keys until removed.
 *
 * SETUP: add 'admin_key' to secrets.php (see secrets.example.php). One key
 * guards everything here, so make it long and keep it private.
 */

$CFG    = is_file(__DIR__ . '/secrets.php') ? (require __DIR__ . '/secrets.php') : [];
$SECRET = is_array($CFG) ? ($CFG['admin_key'] ?? '') : '';

// Fail closed: no configured key → deny everyone.
$KEY = (string)($_GET['key'] ?? $_POST['key'] ?? '');
if ($SECRET === '' || !hash_equals($SECRET, $KEY)) {
  http_response_code(403);
  header('Content-Type: text/plain'); echo 'Forbidden'; exit;
}

// The two submission stores share one shape: an active .jsonl plus an
// append-only archive, with download / archive / download+archive actions.
$STORES = [
  'flags' => [
    'file'    => __DIR__ . '/../patente_flags/flags.jsonl',
    'archive' => __DIR__ . '/../patente_flags/flags-archive.jsonl',
    'stem'    => 'patente-flags',
  ],
  'bugs' => [
    'file'    => __DIR__ . '/../patente_bugs/bugs.jsonl',
    'archive' => __DIR__ . '/../patente_bugs/bugs-archive.jsonl',
    'stem'    => 'patente-bugs',
  ],
];
$SYNC_DIR = __DIR__ . '/../patente_sync';

$which = (string)($_GET['store'] ?? $_POST['store'] ?? '');
$store = $STORES[$which] ?? null;
$action = (string)($_GET['action'] ?? $_POST['action'] ?? '');

// ── Actions on a submission store (flags or bugs) ─────────────────────
if ($store && $action === 'download') {
  header('Content-Type: text/plain; charset=utf-8');
  header('Content-Disposition: attachment; filename="' . $store['stem'] . '-' . gmdate('Ymd-His') . '.jsonl"');
  if (is_file($store['file'])) readfile($store['file']);
  exit;
}
if ($store && $action === 'download_archive') {
  header('Content-Type: text/plain; charset=utf-8');
  header('Content-Disposition: attachment; filename="' . $store['stem'] . '-archive-' . gmdate('Ymd-His') . '.jsonl"');
  if (is_file($store['archive'])) readfile($store['archive']);
  exit;
}
// Destructive actions are POST-only so a prefetch or scanner can never fire them.
if ($store && $_SERVER['REQUEST_METHOD'] === 'POST' && $action === 'archive') {
  if (is_file($store['file']) && filesize($store['file']) > 0) {
    @file_put_contents($store['archive'], @file_get_contents($store['file']), FILE_APPEND | LOCK_EX);
    @file_put_contents($store['file'], '', LOCK_EX);
  }
  header('Location: admin.php?key=' . urlencode($SECRET) . '#' . $which); exit;
}
// One step: stream the current submissions as a download AND move them to the
// archive. The archive always keeps a copy, so a failed download loses nothing.
if ($store && $_SERVER['REQUEST_METHOD'] === 'POST' && $action === 'download_and_archive') {
  $data = (is_file($store['file']) && filesize($store['file']) > 0) ? (string)@file_get_contents($store['file']) : '';
  if ($data !== '') {
    @file_put_contents($store['archive'], $data, FILE_APPEND | LOCK_EX);
    @file_put_contents($store['file'], '', LOCK_EX);
  }
  header('Content-Type: text/plain; charset=utf-8');
  header('Content-Disposition: attachment; filename="' . $store['stem'] . '-' . gmdate('Ymd-His') . '.jsonl"');
  echo $data;
  exit;
}

// ── Gather data for the page ──────────────────────────────────────────
// Reply links (2026-09-24). A bug report may carry the address its writer typed
// in; a trusted reviewer's address lives in secrets.php only, looked up here by
// display name. Either way the link just opens your own mail program: this
// page sends nothing.
$REVIEWER_EMAILS = [];
foreach ((array)(is_array($CFG) ? ($CFG['reviewers'] ?? []) : []) as $code => $ent) {
  if (is_array($ent) && !empty($ent['email'])) $REVIEWER_EMAILS[(string)($ent['name'] ?? $code)] = (string)$ent['email'];
}
function reply_link($email, $subject) {
  if (!$email || !filter_var($email, FILTER_VALIDATE_EMAIL)) return '';
  return '<a class="reply" href="mailto:' . htmlspecialchars(rawurlencode($email), ENT_QUOTES)
    . '?subject=' . htmlspecialchars(rawurlencode($subject), ENT_QUOTES) . '">✉ Reply to '
    . htmlspecialchars($email) . '</a>';
}

function read_records($file) {
  $lines = is_file($file) ? array_values(array_filter(array_map('trim', file($file)))) : [];
  $records = [];
  foreach ($lines as $ln) { $r = json_decode($ln, true); if ($r) $records[] = $r; }
  usort($records, function ($a, $b) {
    $ta = !empty($a['trusted']) ? 1 : 0; $tb = !empty($b['trusted']) ? 1 : 0;
    if ($ta !== $tb) return $tb - $ta;
    return strcmp((string)($b['ts'] ?? ''), (string)($a['ts'] ?? ''));
  });
  return $records;
}
function archive_count($file) {
  return is_file($file) ? count(array_filter(array_map('trim', file($file)))) : 0;
}

$flagRecords = read_records($STORES['flags']['file']);
$bugRecords  = read_records($STORES['bugs']['file']);

$now = time();
$buckets = [];
$users = [];   // one row per bucket, for the per-user table
foreach ((array)@glob($SYNC_DIR . '/*.json') as $f) {
  if (!preg_match('/\/([a-f0-9]{64})\.json$/', $f, $mm)) continue;
  $mt = (int)@filemtime($f);
  $buckets[] = $mt;
  // The sidecar written by sync.php since 2026-09-27; older buckets lack it
  // until their next upload, so first-seen and the counts show as unknown.
  $meta = @json_decode((string)@file_get_contents($SYNC_DIR . '/' . $mm[1] . '.meta.json'), true);
  $users[] = [
    'id'     => substr($mm[1], 0, 8),
    'last'   => $mt,
    'first'  => is_array($meta) && !empty($meta['first']) ? strtotime($meta['first']) : null,
    'pushes' => is_array($meta) ? (int)($meta['pushes'] ?? 0) : null,
    'days'   => is_array($meta) ? count((array)($meta['days'] ?? [])) : null,
    'size'   => (int)@filesize($f),
  ];
}
usort($users, fn($a, $b) => $b['last'] - $a['last']);
function ago($t, $now) {
  $d = $now - $t;
  if ($d < 3600) return max(1, intdiv($d, 60)) . ' min ago';
  if ($d < 86400) return intdiv($d, 3600) . ' h ago';
  return intdiv($d, 86400) . ' d ago';
}
$within = fn($days) => count(array_filter($buckets, fn($m) => $m >= $now - $days * 86400));

$k = htmlspecialchars($SECRET, ENT_QUOTES);
header('Content-Type: text/html; charset=utf-8');
header('Cache-Control: no-store');
?><!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Patente — admin</title>
<style>
  body { font: 15px system-ui, sans-serif; margin: 1.5rem auto; max-width: 820px; padding: 0 1rem; color: #1a1a1a; }
  h1 { font-size: 1.35rem; }
  h2.sect { font-size: 1.1rem; margin: 2rem 0 .5rem; padding-top: 1rem; border-top: 2px solid #eee; }
  table.stats { border-collapse: collapse; }
  table.stats td { padding: .35rem .8rem .35rem 0; }
  table.stats td:last-child { text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; }
  .bar a { margin-right: 1rem; }
  .bar form { display: inline; margin-right: 1rem; }
  .bar button.linklike { background: none; border: 0; padding: 0; margin: 0; color: #0645ad; font: inherit; text-decoration: underline; cursor: pointer; }
  article { border: 1px solid #ddd; border-radius: 10px; padding: .7rem 1rem; margin: .9rem 0; }
  h3 { font-size: 1rem; margin: .5rem 0 .2rem; }
  .muted { color: #777; font-size: .85em; }
  .note { background: #fff7e6; border-left: 3px solid #e0a000; padding: .3rem .6rem; margin: .3rem 0; }
  .report { white-space: pre-wrap; margin: .3rem 0; }
  .ctx { color: #777; font-size: .8em; }
  article.trusted { border-color: #1f9d55; box-shadow: 0 0 0 1px #1f9d55 inset; }
  .badge { display: inline-block; font-size: .72rem; font-weight: 700; padding: .1rem .45rem; border-radius: 999px; vertical-align: middle; }
  .badge.t { background: #1f9d55; color: #fff; }
  .badge.u { background: #eee; color: #777; }
  nav.jump a { margin-right: 1rem; }
  .badge.q { background: #3a5fd0; color: #fff; }
  a.reply { font-weight: 600; }
  table.users { border-collapse: collapse; width: 100%; margin-top: 1rem; font-size: .9em; }
  table.users th, table.users td { padding: .3rem .5rem; border-bottom: 1px solid #eee; text-align: left; white-space: nowrap; }
  table.users td.n { text-align: right; font-variant-numeric: tabular-nums; }
  table.users tr.stale td { color: #999; }
</style>
<h1>Patente — admin</h1>
<nav class="jump">
  <a href="#sync">Sync (<?= count($buckets) ?>)</a>
  <a href="#flags">Flags (<?= count($flagRecords) ?>)</a>
  <a href="#bugs">Bugs (<?= count($bugRecords) ?>)</a>
</nav>

<h2 class="sect" id="sync">Sync store</h2>
<table class="stats">
  <tr><td>Sync users (total buckets)</td><td><?= count($buckets) ?></td></tr>
  <tr><td>Active in the last 24 hours</td><td><?= $within(1) ?></td></tr>
  <tr><td>Active in the last 7 days</td><td><?= $within(7) ?></td></tr>
  <tr><td>Active in the last 30 days</td><td><?= $within(30) ?></td></tr>
  <tr><td>Newest sync</td><td><?= $buckets ? gmdate('Y-m-d H:i', max($buckets)) . ' UTC' : '—' ?></td></tr>
</table>
<p class="muted">Each bucket is one user's end-to-end encrypted sync; contents are never read.
Counts only users who enabled Sync — a lower bound on active users.</p>

<?php if ($users): ?>
<table class="users">
  <tr><th>User</th><th>Last sync</th><th></th><th>First sync</th><th>Days active</th><th>Uploads</th><th>Size</th></tr>
  <?php foreach ($users as $u): ?>
  <tr class="<?= $u['last'] >= $now - 7 * 86400 ? '' : 'stale' ?>">
    <td><code><?= htmlspecialchars($u['id']) ?></code></td>
    <td><?= gmdate('Y-m-d H:i', $u['last']) ?> UTC</td>
    <td class="muted"><?= ago($u['last'], $now) ?></td>
    <td><?= $u['first'] ? gmdate('Y-m-d', $u['first']) : '<span class="muted">before tracking</span>' ?></td>
    <td class="n"><?= $u['days'] === null ? '—' : $u['days'] ?></td>
    <td class="n"><?= $u['pushes'] === null ? '—' : $u['pushes'] ?></td>
    <td class="n"><?= number_format($u['size'] / 1024, 0) ?> KB</td>
  </tr>
  <?php endforeach; ?>
</table>
<p class="muted">One row per synced user, newest first; the ID is the start of the bucket hash, not
the sync code. "Last sync" is the last upload, which happens after the user answers something, so
opening the app without studying does not move it. Rows older than 7 days are grayed.
First sync, days active and uploads are recorded from 2026-09-27; a user shows "before tracking"
until their next upload, and their counts start then.</p>
<?php endif; ?>

<?php
// The two submission sections share their rendering chrome; only the article
// body differs, so each passes a renderer for one record.
$sections = [
  ['id' => 'flags', 'title' => 'Flagged questions', 'records' => $flagRecords, 'render' => function ($r) { ?>
      <?php if (!empty($r['note'])): ?><div class="note"><strong>Submission note:</strong> <?= htmlspecialchars($r['note']) ?></div><?php endif; ?>
      <?php foreach ($r['flags'] ?? [] as $f): ?>
        <h3>#<?= htmlspecialchars($f['number'] ?? '?') ?> — <?php if (($f['category'] ?? '') === 'question'): ?><span class="badge q">QUESTION</span><?php else: ?><?= htmlspecialchars($f['category'] ?? '') ?><?php endif; ?> <span class="muted">(<?= htmlspecialchars($f['answer'] ?? '') ?>)</span></h3>
        <?php if (!empty($f['italian'])): ?><div><?= htmlspecialchars($f['italian']) ?></div><?php endif; ?>
        <?php if (!empty($f['english'])): ?><div class="muted"><?= htmlspecialchars($f['english']) ?></div><?php endif; ?>
        <?php if (!empty($f['note'])): ?><div class="note"><?= htmlspecialchars($f['note']) ?></div><?php endif; ?>
      <?php endforeach; ?>
  <?php }],
  ['id' => 'bugs', 'title' => 'Bug reports', 'records' => $bugRecords, 'render' => function ($r) { $c = $r['context'] ?? []; ?>
      <div class="report"><?= htmlspecialchars($r['report'] ?? '') ?></div>
      <?php if (!empty($r['email'])): ?><div><?= reply_link($r['email'], 'Your Patente B bug report') ?></div><?php else: ?><div class="muted">No reply address given.</div><?php endif; ?>
      <div class="ctx">v<?= htmlspecialchars($c['version'] ?? '?') ?> · level <?= htmlspecialchars($c['level'] ?? '?') ?> · <?= htmlspecialchars($c['screen'] ?? '?') ?> · <?= htmlspecialchars($c['lang'] ?? '?') ?><br><?= htmlspecialchars($c['ua'] ?? '') ?></div>
  <?php }],
];
foreach ($sections as $s):
  $meta = $STORES[$s['id']]; ?>
<h2 class="sect" id="<?= $s['id'] ?>"><?= $s['title'] ?> (<?= count($s['records']) ?> active)</h2>
<div class="bar">
  <?php if ($s['records']): ?>
  <form method="post" onsubmit="return confirm('Download these <?= count($s['records']) ?> item(s) and move them to the archive (clearing the active list)?')">
    <input type="hidden" name="key" value="<?= $k ?>">
    <input type="hidden" name="store" value="<?= $s['id'] ?>">
    <input type="hidden" name="action" value="download_and_archive">
    <button type="submit" class="linklike">Download &amp; archive (<?= count($s['records']) ?>)</button>
  </form>
  <?php else: ?><span class="muted">Nothing new.</span> <?php endif; ?>
  <?php if (is_file($meta['archive'])): ?><a href="?key=<?= $k ?>&store=<?= $s['id'] ?>&action=download_archive">Download full archive (<?= archive_count($meta['archive']) ?>)</a><?php endif; ?>
</div>
<?php foreach ($s['records'] as $r): ?>
  <article class="<?= !empty($r['trusted']) ? 'trusted' : '' ?>">
    <div class="muted">
      <?php if (!empty($r['trusted'])): ?><span class="badge t">TRUSTED</span> <?php elseif (!empty($r['reviewer'])): ?><span class="badge u">unverified</span> <?php endif; ?>
      <?php if (!empty($r['reviewer'])): ?><strong><?= htmlspecialchars($r['reviewer']) ?></strong> · <?php endif; ?>
      <?= htmlspecialchars($r['ts'] ?? '') ?><?php if (isset($r['version'])): ?> · v<?= htmlspecialchars($r['version']) ?><?php endif; ?>
      <?php if (!empty($r['trusted']) && isset($REVIEWER_EMAILS[$r['reviewer'] ?? ''])): ?> · <?= reply_link($REVIEWER_EMAILS[$r['reviewer']], 'Your Patente B review comments') ?><?php endif; ?></div>
    <?php ($s['render'])($r); ?>
  </article>
<?php endforeach; ?>
<?php endforeach; ?>
</html>
