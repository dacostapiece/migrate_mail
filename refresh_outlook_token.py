#!/usr/bin/env python3
"""
Refreshes the Outlook.com OAuth2 access token used by imapsync, by talking
directly to Microsoft's token endpoint with the refresh_token grant.

Why this exists: oauth2_imap.exe (the vendor tool) does the interactive
browser sign-in fine, but its own post-auth IMAP self-check fails with a
TLS certificate verification error in this environment, and it refuses to
save the token file unless that self-check passes. This script bypasses
that broken self-check entirely - it only needs a valid refresh_token
(no IMAP connection, no interactive browser) and writes the token file in
the exact format imapsync/oauth2_imap expect: line 1 = access_token,
line 2 = refresh_token.

Uses Thunderbird's public client_id (no client secret involved, PKCE-style
public client), same as oauth2_imap.exe's default.
"""

import json
import ssl
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# This machine's local TLS interception (antivirus/security software) injects
# a CA certificate with a malformed Basic Constraints extension, which fails
# strict verification. imapsync itself already runs with SSL_verify_mode=0
# for the same reason, so this matches that existing trust posture.
_UNVERIFIED_SSL_CONTEXT = ssl._create_unverified_context()

CLIENT_ID = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"  # Thunderbird public client
TOKEN_URI = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
SCOPE = "offline_access https://outlook.office.com/IMAP.AccessAsUser.All"
USER = "mymailaccount@outlook.com.br"

TOKEN_FILE = (
    Path(__file__).resolve().parent.parent
    / "oauth2_imap" / "tokens"
    / f"oauth2_tokens_thunderbird_office365_{USER}.txt"
)


def read_refresh_token(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 2 or not lines[1].strip():
        raise SystemExit(f"No refresh token found on line 2 of {path}")
    return lines[1].strip()


def write_tokens(path: Path, access_token: str, refresh_token: str) -> None:
    content = "\n".join([
        access_token,
        refresh_token,
        "# The first   line is the access  token",
        "# The second  line is the refresh token",
        f"# Account is {USER}",
        f"# Refreshed on {datetime.now()} by refresh_outlook_token.py",
        "",
    ])
    path.write_text(content, encoding="utf-8")


def refresh(refresh_token: str) -> tuple[str, str]:
    import urllib.parse as _parse
    body = _parse.urlencode({
        "client_id": CLIENT_ID,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "scope": SCOPE,
    }).encode("ascii")

    req = urllib.request.Request(TOKEN_URI, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=30, context=_UNVERIFIED_SSL_CONTEXT) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Token refresh failed ({e.code}): {detail}")

    access_token = payload.get("access_token")
    new_refresh_token = payload.get("refresh_token", refresh_token)
    if not access_token:
        raise SystemExit(f"No access_token in response: {payload}")
    return access_token, new_refresh_token


def main() -> int:
    if not TOKEN_FILE.exists():
        print(f"[FAILED] Token file not found: {TOKEN_FILE}")
        return 1

    old_refresh_token = read_refresh_token(TOKEN_FILE)
    access_token, new_refresh_token = refresh(old_refresh_token)
    write_tokens(TOKEN_FILE, access_token, new_refresh_token)
    print(f"[OK] Access token refreshed, written to {TOKEN_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
