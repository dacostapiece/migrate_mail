@ECHO OFF
SETLOCAL EnableDelayedExpansion
PUSHD %~dp0

REM ============================================================
REM  Reusable UOL -> Outlook sync (mymailaccounta@uol.com.br -> mymailaccounta@outlook.com.br)
REM  Safe to run again any time to pick up new UOL mail: imapsync
REM  only adds messages, it never deletes/expunges on either side,
REM  and skips anything already copied. See README.md for the full
REM  story on why each flag below is needed.
REM ============================================================

SET MAX_RETRIES=100
SET attempt=0

:retry
SET /A attempt+=1
ECHO.
ECHO ==================== Sync attempt %attempt% of %MAX_RETRIES% ====================

REM --- Refresh the Outlook OAuth2 token (no browser needed in normal use) ---
python refresh_outlook_token.py
IF ERRORLEVEL 1 (
  ECHO.
  ECHO [FAILED] Could not refresh the OAuth2 token. The refresh token itself
  ECHO may have expired/been revoked ^(rare - normally lasts weeks/months and
  ECHO rotates on every use^). See README.md: "Bootstrapping a brand new token".
  GOTO :done
)

REM --- Run the actual sync ---
..\imapsync.exe ^
  --host1 imap.uol.com.br --user1 mymailaccounta@uol.com.br --passfile1 passfile1.txt --ssl1 --port1 993 --sslargs1 SSL_version=TLSv1_2 ^
  --host2 outlook.office365.com --user2 mymailaccounta@outlook.com.br --oauthaccesstoken2 ..\oauth2_imap\tokens\oauth2_tokens_thunderbird_office365_mymailaccounta@outlook.com.br.txt ^
  --automap --syncinternaldates --useheader "Message-Id" --errorsmax 500

IF NOT ERRORLEVEL 1 (
  ECHO.
  ECHO [DONE] imapsync finished cleanly - fully in sync.
  GOTO :done
)

IF !attempt! GEQ %MAX_RETRIES% (
  ECHO.
  ECHO [STOPPED] Reached max retries ^(%MAX_RETRIES%^). Check the latest log in
  ECHO           LOG_imapsync\ before re-running this script.
  GOTO :done
)

ECHO.
ECHO imapsync stopped early ^(usually token expiry mid-run, or Microsoft's
ECHO IMAP throttling - "Server Unavailable" - after sustained activity^).
ECHO Refreshing token and resuming in 90 seconds, to let any throttling
ECHO cool down... ^(Ctrl+C to abort^)
TIMEOUT /T 90
GOTO :retry

:done
POPD
PAUSE
