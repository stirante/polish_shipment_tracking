import asyncio
import base64
import hashlib
import json
import logging
import secrets
import time
import urllib.parse

import aiohttp
import async_timeout

from .api_helpers import request_json

_LOGGER = logging.getLogger(__name__)

# InPost Mobile signs in through OAuth2 + PKCE on account.inpost-group.com. The
# login page has a Cloudflare captcha and only accepts InPost's own redirect URI,
# so the user signs in in a browser and pastes the URL the login ends on.
AUTHORIZE_URL = "https://account.inpost-group.com/oauth2/authorize"
REDIRECT_URI = "https://account.inpost-group.com/callback"
CLIENT_ID = "inpost-mobile"
APP_ID = "pl.inpost.inmobile"

# Refresh this long before the access token (valid for 2 h) runs out.
EXPIRY_MARGIN = 60


class InPostAuthError(Exception):
    """The session cannot be refreshed; the user has to sign in again."""


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def token_claims(token: str | None) -> dict:
    """Return the unverified payload of a JWT, or {} when it is not one."""
    parts = str(token or "").split(".")
    if len(parts) != 3:
        return {}
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    try:
        claims = json.loads(base64.urlsafe_b64decode(payload))
    except (ValueError, TypeError):
        return {}
    return claims if isinstance(claims, dict) else {}


def token_phone(token: str | None) -> str | None:
    """Return the 9-digit phone number an InPost access token was issued for."""
    phone = token_claims(token).get("phone")
    return str(phone) if phone else None


class InPostLogin:
    """One sign-in attempt: the login URL and the PKCE secret behind it."""

    def __init__(self):
        self._verifier = _b64url(secrets.token_bytes(48))
        self._state = _b64url(secrets.token_bytes(24))
        self._nonce = _b64url(secrets.token_bytes(24))

    @property
    def verifier(self) -> str:
        return self._verifier

    @property
    def url(self) -> str:
        challenge = _b64url(hashlib.sha256(self._verifier.encode()).digest())
        params = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": "openid",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "state": self._state,
            "nonce": self._nonce,
            "response_mode": "query",
            "lang": "pl-PL",
            # Ask for the sign-in form even when the browser still has an
            # InPost session, so a second account does not reuse the first.
            "prompt": "login",
            "supported_markets": "PL",
        }
        return f"{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

    def extract_code(self, pasted: str) -> str:
        """Return the authorization code from the pasted callback URL.

        Raises ValueError("sms") for a pasted SMS code, ValueError("state") for
        a URL from another sign-in attempt and ValueError("no_code") otherwise.
        """
        value = str(pasted or "").strip()
        if "code=" not in value:
            raise ValueError("sms" if value.replace(" ", "").isdigit() else "no_code")
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(value).query or value)
        code = (query.get("code") or [""])[0]
        if not code:
            raise ValueError("no_code")
        state = (query.get("state") or [None])[0]
        if state is not None and state != self._state:
            raise ValueError("state")
        return code


class InPostApi:
    BASE_URL = "https://api-inmobile-pl.easypack24.net"
    TOKEN_PATH = "global/oauth2/token"

    def __init__(self, session: aiohttp.ClientSession, device_uid: str | None = None):
        self._session = session
        self._token = None
        self._refresh_token = None
        self._expires_at = 0
        self._device_uid = device_uid
        # Parallel requests that all hit an expired token must refresh it once.
        self._refresh_lock = asyncio.Lock()

    def _headers(self) -> dict:
        headers = {
            "User-Agent": "InPost-Mobile",
            "Accept": "application/json",
            "X-App-Id": APP_ID,
        }
        if self._device_uid:
            headers["device-uid"] = self._device_uid
        return headers

    async def request(self, method, path, data=None, headers=None):
        if self._refresh_token and time.time() > self._expires_at - EXPIRY_MARGIN:
            await self.refresh_token(seen_token=self._token)

        request_headers = {**self._headers(), "Content-Type": "application/json"}
        if self._token:
            request_headers["Authorization"] = f"Bearer {self._token}"
        request_headers.update(headers or {})

        return await request_json(
            self._session,
            method,
            f"{self.BASE_URL}/{path.lstrip('/')}",
            json_data=data,
            headers=request_headers,
            label="InPost",
            log_401_as_info=True,
            error_with_text=True,
        )

    async def _token_request(self, form: dict) -> dict:
        """POST to the OAuth token endpoint and store the returned tokens."""
        url = f"{self.BASE_URL}/{self.TOKEN_PATH}"
        headers = {**self._headers(), "Content-Type": "application/x-www-form-urlencoded"}
        try:
            async with async_timeout.timeout(30):
                async with self._session.post(url, data=form, headers=headers) as resp:
                    text = await resp.text()
                    if resp.status in (400, 401, 403):
                        # invalid_grant: the code or refresh token is used up or revoked.
                        _LOGGER.info("InPost token endpoint rejected the grant: %s %s", resp.status, text)
                        raise InPostAuthError(f"InPost token endpoint {resp.status}: {text}")
                    if resp.status >= 400:
                        raise Exception(f"InPost token endpoint {resp.status}: {text}")
        except asyncio.TimeoutError as err:
            raise Exception("InPost token request timed out") from err
        except aiohttp.ClientError as err:
            raise Exception(f"InPost token request failed: {err}") from err

        try:
            payload = json.loads(text)
        except ValueError as err:
            raise Exception(f"InPost token endpoint returned no JSON: {text[:200]}") from err
        if not payload.get("access_token") or not payload.get("refresh_token"):
            raise InPostAuthError("InPost token response has no tokens")

        self._token = payload["access_token"]
        self._refresh_token = payload["refresh_token"]
        self._expires_at = time.time() + float(payload.get("expires_in") or 0)
        return payload

    async def exchange_code(self, code: str, verifier: str) -> dict:
        """Trade the authorization code from the callback URL for tokens."""
        return await self._token_request(
            {
                "client_id": CLIENT_ID,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
                "code_verifier": verifier,
                "code": code,
            }
        )

    async def refresh_token(self, seen_token: str | None = None):
        """Refresh the InPost token.

        With seen_token, skip the refresh when another request already replaced
        that token while this one waited for the lock.
        """
        async with self._refresh_lock:
            if seen_token is not None and self._token != seen_token:
                return
            if not self._refresh_token:
                raise InPostAuthError("Missing InPost refresh token")
            await self._token_request(
                {
                    "client_id": CLIENT_ID,
                    "grant_type": "refresh_token",
                    "refresh_token": self._refresh_token,
                }
            )

    async def get_parcels(self):
        """Fetch all tracked parcels, following API pagination until all pages are retrieved."""
        all_parcels = []
        cursor = None
        has_more = True
        max_pages = 20

        while has_more and max_pages > 0:
            max_pages -= 1
            path = "v4/parcels/tracked"
            if cursor:
                path = f"v4/parcels/tracked?updatedAfter={urllib.parse.quote(str(cursor), safe=':')}"

            data = await self.request("GET", path)
            if not data:
                break

            if isinstance(data, list):
                all_parcels.extend(data)
                break

            if isinstance(data, dict):
                batch = data.get("parcels", [])
                if isinstance(batch, list):
                    all_parcels.extend(batch)
                has_more = bool(data.get("more"))
                cursor = data.get("updatedUntil")
                if not cursor or not batch:
                    break
            else:
                break

        # Deduplicate parcels while preserving order. Later pages hold
        # parcels updated after the earlier ones, so the last copy wins.
        index_by_id = {}
        unique_parcels = []
        for p in all_parcels:
            if isinstance(p, dict):
                pid = p.get("shipmentNumber")
                if pid and pid in index_by_id:
                    unique_parcels[index_by_id[pid]] = p
                    continue
                if pid:
                    index_by_id[pid] = len(unique_parcels)
                unique_parcels.append(p)

        return unique_parcels

    async def get_parcel(self, shipment_number: str):
        encoded = urllib.parse.quote(str(shipment_number), safe="")
        return await self.request("GET", f"v4/parcels/tracked/{encoded}")
