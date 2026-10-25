<?php
/**
 * Template for the private configuration the PHP endpoints read.
 *
 * SETUP: copy this file to `secrets.php` (which is gitignored) and fill in your
 * own values, then upload `secrets.php` to the server. If `secrets.php` is absent,
 * the admin page denies all access (fail closed) and no reviewers are trusted.
 *
 * Generate a strong admin key, e.g.:
 *   php -r "echo bin2hex(random_bytes(20)), PHP_EOL;"
 */
return [
  // Must equal APP_SUBMIT_TOKEN in app.js. NOT a secret (visible in the client);
  // it only deters trivial bots.
  'submit_token' => 'PUT_THE_APP_SUBMIT_TOKEN_HERE',
  // Key for the unified admin page (admin.php) — keep it secret.
  'admin_key' => 'PUT_A_LONG_RANDOM_STRING_HERE',
  // Trusted reviewers. Either 'code' => 'Display name', or, to get a
  // "reply by email" link beside their comments in admin.php,
  // 'code' => ['name' => 'Display name', 'email' => 'them@example.com'].
  // The email never leaves this file. Leave empty for none.
  // Where to email a copy of each bug report and each batch of reviewer
  // comments. Leave out (or empty) for no email. 'notify_from' is the sender
  // and should be an address on this site's domain; it defaults to
  // noreply@<domain>.
  'notify_email' => '',
  // 'notify_from' => 'noreply@example.com',
  'reviewers' => [
    // 'friend-xxxxxxxx' => 'Friend name',
    // 'friend-yyyyyyyy' => ['name' => 'Friend name', 'email' => 'friend@example.com'],
  ],
];
