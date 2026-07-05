# UOL <-> Outlook sync (Windows, native)

Copies mail from mymailaccount@uol.com.br to mymailaccount@outlook.com.br.
Additive only - never deletes or expunges anything on either side, and
skips messages already copied, so it's always safe to run again (e.g. to
pick up new UOL mail later).

## What's actually needed for future syncs

Just two things, both in this folder:

- **`sync_uol_to_outlook.bat`** - the one script to run. Refreshes the
  Outlook token, then runs the real imapsync transfer, retrying
  automatically (up to 100 times, 90s apart) if it gets interrupted.
- **`refresh_outlook_token.py`** - a small Python script the batch file
  calls to keep the Outlook OAuth2 token alive. Needs Python 3 (already
  on this machine) and no third-party packages (stdlib only).

Everything else in `imapsync_2.264\` (the `oauth2_imap\` folder,
`imapsync.exe`, the old staged `0X_*.bat` scripts) is either a one-time
bootstrap dependency or leftover troubleshooting scaffolding - see below.

## One-time setup (already done, kept here for reference)

1. `passfile1.txt` in this folder holds the plain UOL webmail password
   (imapsync reads it via `--passfile1`, so it's never on the command line).
2. `..\oauth2_imap\tokens\oauth2_tokens_thunderbird_office365_mymailaccount@outlook.com.br.txt`
   holds the Outlook OAuth2 tokens (access token on line 1, refresh token
   on line 2). This is what `refresh_outlook_token.py` reads and rewrites
   every run. If this file is ever lost, see "Bootstrapping a brand new
   token" below.

## The two problems we hit, and the fixes baked into the script

### 1. Outlook OAuth2: the vendor's own token tool silently failed to save

`imapsync` can't do OAuth2 itself - it only consumes a pre-generated
access token via `--oauthaccesstoken2 <file>`. The vendor ships a helper
for this, `oauth2_imap.exe`, which does an interactive browser sign-in
using **Thunderbird's public client ID** (`9e5f94bc-e8a4-4e73-b8be-63364c29d753`)
- a real public OAuth2 client using PKCE, no client secret, already
consented for IMAP on any Microsoft account. That part works fine.

The problem: after getting a token, `oauth2_imap.exe` does its own
internal check - a real IMAP connection with full TLS certificate
verification - before it will save the token to file. On this machine
that check fails with a TLS certificate error, because local
security/antivirus software intercepts HTTPS traffic with a root
certificate that strict TLS validation rejects. So the tool would obtain
a perfectly valid token, print it to the console, and then refuse to
persist it because its own paranoid self-check failed.

(We also tried the older `oauth2_office365_with_imap.exe` shipped in this
install - that one uses a *different*, non-Thunderbird Azure app
[`c46947ca-867f-...`] which turned out to have an expired/invalid client
secret server-side (`AADSTS7000215`). Not fixable on our end either way,
which is why we moved to `oauth2_imap.exe`/Thunderbird's client ID.)

**Fix:** `refresh_outlook_token.py` bypasses `oauth2_imap.exe`'s self-check
entirely. It talks directly to Microsoft's token endpoint
(`login.microsoftonline.com/common/oauth2/v2.0/token`) using the
`refresh_token` grant, the same Thunderbird client ID, and no IMAP
connection at all - just an HTTPS POST, response parsed, token file
rewritten. Since imapsync itself already runs with `SSL_verify_mode=0`
(doesn't verify certificates) for the exact same local-interception
reason, the script matches that same trust posture and disables cert
verification for its one HTTPS call too.

This only works for *refreshing* an existing refresh token. If the
refresh token itself ever expires/is revoked (rare - it lasts weeks to
months and Microsoft rotates it on every use, extending its life), you
need a fresh interactive sign-in - see "Bootstrapping a brand new token".

### 2. UOL: TLS handshake resets unless pinned to TLS 1.2

Connecting to `imap.uol.com.br:993` failed at the TLS handshake itself
(`SSL connect attempt failed`, or a raw `errno=10054` connection reset
with plain `openssl s_client`) - this happened even with certificate
verification off, so it wasn't a trust problem. Forcing TLS 1.3 also
reset; forcing TLS 1.2 connected cleanly with a normal Dovecot banner.
UOL's mail server apparently can't handle a TLS 1.3 handshake and hard
resets instead of negotiating down, while modern OpenSSL/Perl try 1.3
first by default.

**Fix:** `--ssl1 --port1 993 --sslargs1 SSL_version=TLSv1_2` forces the
UOL side onto TLS 1.2 explicitly instead of relying on auto-negotiation.

### 3. Microsoft IMAP throttling on long runs

On a long transfer, Outlook's IMAP backend starts returning
`NO Server Unavailable` - Exchange Online throttling a mailbox that's
been doing sustained APPEND traffic for a while. Combined with the
access token expiring after ~1 hour, a single multi-hour run can
accumulate errors. Two mitigations are baked into the script:

- `--errorsmax 500` - the default is 50, which is too low; most of these
  errors are transient (throttling, or a token expiring mid-run) and the
  same messages go through fine on a later pass.
- The retry loop waits 90 seconds between attempts (not just a few
  seconds) to give Microsoft's throttling window time to reset, and
  allows up to 100 attempts for a very large initial migration.

None of this needed a support ticket or plan change - it just needs
patience and re-running.

## Running a sync

Double-click `sync_uol_to_outlook.bat`, or from a terminal:

```
cd /d "%userprofile%\uol_to_outlook\subfolder"
sync_uol_to_outlook.bat
```

Leave the window open. It refreshes the token, runs the transfer, and
automatically retries on interruption. When it prints
`[DONE] imapsync finished cleanly - fully in sync.`, there's nothing left
to copy. Logs land in `LOG_imapsync\` in this folder, named by timestamp.

## Bootstrapping a brand new token (only if the refresh token dies)

This should be rare - only needed if the token file is lost, or the
refresh token expires from months of disuse. To get a fresh one:

1. Run `..\oauth2_imap\oauth2_imap.exe --token_file ..\oauth2_imap\tokens\oauth2_tokens_thunderbird_office365_mymailaccount@outlook.com.br.txt mymailaccount@outlook.com.br`
   from inside the `oauth2_imap` folder (it needs `localhost.crt`/`localhost.key`
   next to it for its HTTPS redirect listener).
2. A browser window opens for Microsoft sign-in. Known hiccups:
   - Browser warns about an insecure/self-signed `localhost` certificate -
     expected, click through ("Advanced" -> "Proceed").
   - Script gets stuck at "Connection accepted" - click into the browser's
     address bar (the `https://localhost:PORT/?code=...` URL) and press
     ENTER to force a re-request.
   - Browser flags the redirect as phishing and hangs (a known imapsync
     issue, GitHub #521) - close the tab, retry, or use an incognito window.
3. This step will likely also fail with the same TLS self-check error
   described above (that's expected and fine) - as long as the console
   printed a real `access_token`/`refresh_token` pair before that, manually
   copy those two values into the token file: line 1 = access token,
   line 2 = refresh token. `sync_uol_to_outlook.bat` takes it from there.
