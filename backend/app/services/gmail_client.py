"""
Gmail integration - READ-ONLY by design.

This app never sends email on the user's behalf. It only:
1. Reads recent messages (gmail.readonly scope - can't send, delete, or modify)
2. Uses AI to categorize them (recruiter response / interview invite /
   scholarship decision / other)
3. Generates a suggested reply the person can copy and send themselves

This requires a DIFFERENT OAuth client than the "Continue with Google"
sign-in button - that one uses Google Identity Services and needs no
secret. This one needs a real confidential OAuth client (Client ID +
Client Secret) because reading Gmail requires a genuine server-side
token exchange, not just an identity check.

Setup: Google Cloud Console -> APIs & Services -> Credentials -> the
existing OAuth client (or a new one) -> add gmail_redirect_uri as an
Authorized redirect URI -> enable the Gmail API for the project.
"""
import datetime as dt
import base64
from urllib.parse import urlencode

import httpx

from app.config import settings

AUTH_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"

SCOPES = "https://www.googleapis.com/auth/gmail.readonly openid email"


def build_auth_url(state: str) -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.gmail_redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return f"{AUTH_BASE_URL}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.gmail_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def refresh_access_token(refresh_token: str) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            TOKEN_URL,
            data={
                "refresh_token": refresh_token,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "grant_type": "refresh_token",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def get_user_email(access_token: str) -> str | None:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if resp.status_code != 200:
            return None
        return resp.json().get("email")


def _decode_header(headers: list[dict], name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


async def list_recent_messages(access_token: str, max_results: int = 15) -> list[dict]:
    async with httpx.AsyncClient(timeout=20) as client:
        list_resp = await client.get(
            f"{GMAIL_API_BASE}/messages",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"maxResults": max_results, "q": "in:inbox"},
        )
        if list_resp.status_code != 200:
            return []
        message_ids = [m["id"] for m in list_resp.json().get("messages", [])]

        results = []
        for mid in message_ids:
            msg_resp = await client.get(
                f"{GMAIL_API_BASE}/messages/{mid}",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"format": "metadata", "metadataHeaders": ["Subject", "From", "Date"]},
            )
            if msg_resp.status_code != 200:
                continue
            data = msg_resp.json()
            headers = data.get("payload", {}).get("headers", [])
            results.append(
                {
                    "id": data.get("id"),
                    "thread_id": data.get("threadId"),
                    "subject": _decode_header(headers, "Subject") or "(no subject)",
                    "sender": _decode_header(headers, "From") or "(unknown sender)",
                    "snippet": data.get("snippet", ""),
                    "received_at": _decode_header(headers, "Date"),
                }
            )
        return results


async def get_message_body(access_token: str, message_id: str) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{GMAIL_API_BASE}/messages/{message_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"format": "full"},
        )
        if resp.status_code != 200:
            return ""
        data = resp.json()

    def extract_text(part: dict) -> str:
        if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
            raw = part["body"]["data"]
            return base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)).decode("utf-8", errors="ignore")
        for sub in part.get("parts", []) or []:
            text = extract_text(sub)
            if text:
                return text
        return ""

    payload = data.get("payload", {})
    return extract_text(payload) or data.get("snippet", "")