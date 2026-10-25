<?php
/**
 * Emails the maintainer when a bug report or a batch of reviewer comments
 * arrives. Included by report-bug.php and submit-flags.php; requesting this
 * file directly defines a function and prints nothing.
 *
 * The RECIPIENT is fixed in secrets.php ('notify_email'), never taken from the
 * request, so the form cannot be used to send mail to anyone else. A
 * submitter's address, when valid, goes only into Reply-To, so replying from
 * the mail app reaches them. Nothing is sent when 'notify_email' is absent.
 *
 * A global cap (NOTIFY_MAX per hour, across all visitors) keeps a flood of
 * submissions from becoming a flood of mail. Submissions over the cap are
 * still stored; only the email is skipped.
 */

const NOTIFY_MAX    = 30;
const NOTIFY_WINDOW = 3600;

// Every outcome is written to notify_log.txt in the store, because every
// failure here is silent by design (the submission is stored either way) and
// "I did not get the email" then has five possible causes with no evidence
// for any of them. One line per call: what happened, and to whom.
function patente_notify_log(string $storeDir, string $line): void {
  @file_put_contents($storeDir . '/notify_log.txt',
    gmdate('Y-m-d H:i:s') . 'Z ' . $line . "\n", FILE_APPEND | LOCK_EX);
}

// The link into admin.php with the key filled in, so the mail is one click
// from the page (maintainer, 2026-09-25). The key travels in a mail to the
// maintainer's own address only, which is where it already lives. Empty when
// no 'admin_key' is set. $store is the admin page's section, 'flags' or 'bugs'.
function patente_admin_link(array $cfg, string $store): string {
  $key = trim((string)($cfg['admin_key'] ?? ''));
  if ($key === '') return '';
  // SERVER_NAME, never HTTP_HOST: the Host header is the client's, and a
  // link carrying the admin key must not be built from it.
  $host = preg_replace('/[^a-z0-9.\-]/i', '', (string)($_SERVER['SERVER_NAME'] ?? ''));
  if ($host === '') return '';
  return 'https://' . $host . '/admin.php?key=' . rawurlencode($key) . '#' . $store;
}

function patente_notify(array $cfg, string $storeDir, string $subject, string $body, string $replyTo = ''): void {
  $to = trim((string)($cfg['notify_email'] ?? ''));
  if ($to === '') { patente_notify_log($storeDir, "skipped: 'notify_email' is not set in secrets.php"); return; }
  if (!filter_var($to, FILTER_VALIDATE_EMAIL)) { patente_notify_log($storeDir, "skipped: 'notify_email' is not a valid address"); return; }
  if (!function_exists('mail')) { patente_notify_log($storeDir, 'skipped: PHP mail() is not available on this host'); return; }

  // Global hourly cap, one small file of timestamps in the (non-public) store.
  $capFile = $storeDir . '/notify_rl.txt';
  $now  = time();
  $hits = is_file($capFile)
    ? array_filter(array_map('intval', explode("\n", trim((string)@file_get_contents($capFile)))), fn($t) => $t > $now - NOTIFY_WINDOW)
    : [];
  if (count($hits) >= NOTIFY_MAX) { patente_notify_log($storeDir, 'skipped: hourly cap of ' . NOTIFY_MAX . ' reached'); return; }
  $hits[] = $now;
  @file_put_contents($capFile, implode("\n", $hits), LOCK_EX);

  // Sender: an address on the site's own domain, so SPF/DKIM set up in cPanel
  // apply. Configurable, defaulting to noreply@<this host>.
  $host = preg_replace('/[^a-z0-9.\-]/i', '', (string)($_SERVER['SERVER_NAME'] ?? 'localhost'));
  $from = trim((string)($cfg['notify_from'] ?? ('noreply@' . preg_replace('/^(www|patente)\./i', '', $host))));
  if (!filter_var($from, FILTER_VALIDATE_EMAIL)) { patente_notify_log($storeDir, "skipped: sender '$from' is not a valid address"); return; }

  $clean = fn($s) => str_replace(["\r", "\n"], ' ', $s);
  $headers = [
    'From: Patente B app <' . $clean($from) . '>',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'MIME-Version: 1.0',
  ];
  if ($replyTo !== '' && filter_var($replyTo, FILTER_VALIDATE_EMAIL)) {
    $headers[] = 'Reply-To: ' . $clean($replyTo);
  }
  $subj = '=?UTF-8?B?' . base64_encode($clean($subject)) . '?=';
  $sent = @mail($to, $subj, $body, implode("\r\n", $headers), '-f' . $from);
  patente_notify_log($storeDir, ($sent ? 'handed to the mail system' : 'mail() returned false') . " for $to from $from: $subject");
}
