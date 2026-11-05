"""myGLS API client."""
from __future__ import annotations

import base64
import hashlib
import hmac
import asyncio
import json
import secrets
import time
import uuid
from urllib.parse import quote, urlencode, urljoin

import aiohttp


class GlsApi:
    """Client for the myGLS mobile API."""

    AZURE_BASE_URL = "https://login.gls-group.net"
    TENANT = "glsgroup"
    CLIENT_ID = "79ba7504-1b19-4145-8251-09e4fca2ec31"
    REDIRECT_URI = "msauth://pl.gls.mygls/9H%2B2MXEWxpwphWNe%2Bd%2Fxmm9CpFw%3D"
    SIGN_IN_POLICY = "B2C_1A_PL_LOCAL_PHONE_SI"
    ID_SCOPES = ["openid", "offline_access"]
    API_SCOPES = [
        "https://glsgroup.onmicrosoft.com/79ba7504-1b19-4145-8251-09e4fca2ec31/default",
        "offline_access",
    ]

    API_KEY = "dev_mobile_E7TW5Kd04e1xUcGvLf3TFPN8csa15oMdXCMQGqqLKs="
    HMAC_SECRET = "Qhb7YyatnA60UoKGiTgdhn1fU0BvD"
    API_BASE = "https://mygls.gls-poland.com.pl/api/v1"
    TRACKING_SHIPMENT_URL = f"{API_BASE}/mygls-tracking/tracking/shipment"
    SESSION_URL = f"{API_BASE}/mygls-user/user/session"

    def __init__(self, session: aiohttp.ClientSession, session_id: str | None = None):
        self._session = session
        self._token: str | None = None
        self._refresh_token: str | None = None
        self._id_token: str | None = None
        self._expires_at = 0
        self._session_id = session_id or str(uuid.uuid4())
        self._session_registered: str | None = None
        self._cookies: dict[str, str] = {}

    async def login(self, phone: str, password: str) -> dict:
        """Log in through Azure B2C and exchange the token into API scopes."""
        verifier, challenge = _make_pkce()
        authorize_url = self._authorize_url(challenge)

        status, _headers, html = await self._web_request("GET", authorize_url)
        if status >= 400:
            raise Exception(f"GLS authorize failed: {status}")

        settings = _extract_var_json(html, "SETTINGS")
        fields = _extract_var_json(html, "SA_FIELDS")
        phone_field = fields["AttributeFields"][0]["ID"]
        password_field = fields["AttributeFields"][1]["ID"]

        self_asserted_url = (
            f"{self.AZURE_BASE_URL}{settings['hosts']['tenant']}/SelfAsserted?"
            f"tx={quote(settings['transId'])}&p={quote(settings['hosts']['policy'])}"
        )
        status, _headers, text = await self._web_request(
            "POST",
            self_asserted_url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-CSRF-TOKEN": settings["csrf"],
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": authorize_url,
            },
            data=urlencode(
                {
                    "request_type": "RESPONSE",
                    phone_field: phone,
                    password_field: password,
                }
            ),
        )
        login_response = _try_json(text)
        if not isinstance(login_response, dict) or login_response.get("status") != "200":
            raise Exception(f"GLS login failed: {status} - {login_response}")

        confirmed_url = (
            f"{self.AZURE_BASE_URL}{settings['hosts']['tenant']}/api/{settings['api']}/confirmed?"
            f"rememberMe=false&csrf_token={quote(settings['csrf'])}"
            f"&tx={quote(settings['transId'])}&p={quote(settings['hosts']['policy'])}"
        )
        final_location = await self._follow_to_msauth(confirmed_url, authorize_url)
        code = _query_param(final_location, "code")
        if not code:
            raise Exception("GLS login redirect did not contain an authorization code")

        id_token_data = await self._exchange_code(code, verifier)
        api_token_data = await self._refresh_oauth_token(
            id_token_data["refresh_token"],
            self.API_SCOPES,
        )

        self._id_token = id_token_data.get("id_token")
        self._token = api_token_data.get("access_token")
        self._refresh_token = api_token_data.get("refresh_token") or id_token_data.get("refresh_token")
        self._expires_at = _jwt_exp(self._token) or int(time.time()) + int(api_token_data.get("expires_in", 3600))
        self._session_registered = None

        await self.ensure_session()
        return self.export_auth_data()

    def export_auth_data(self) -> dict:
        """Return serializable auth data for Home Assistant config entry."""
        return {
            "access_token": self._token,
            "refresh_token": self._refresh_token,
            "id_token": self._id_token,
            "token_expires_at": self._expires_at,
            "session_id": self._session_id,
            "session_registered": self._session_registered,
        }

    async def refresh_token(self) -> dict:
        """Refresh the API access token."""
        if not self._refresh_token:
            raise Exception("GLS refresh token is missing")
        data = await self._refresh_oauth_token(self._refresh_token, self.API_SCOPES)
        self._token = data.get("access_token")
        self._refresh_token = data.get("refresh_token") or self._refresh_token
        self._expires_at = _jwt_exp(self._token) or int(time.time()) + int(data.get("expires_in", 3600))
        return data

    async def ensure_session(self) -> None:
        """Register the current SessionId with the myGLS backend."""
        if self._session_registered == self._session_id:
            return
        await self.request(
            "POST",
            self.SESSION_URL,
            json_data={
                "deviceName": "Home Assistant",
                "deviceType": "ANDROID",
                "sessionId": self._session_id,
            },
            ensure_session=False,
        )
        self._session_registered = self._session_id

    async def get_parcels(self, page: int = 0, limit: int = 100, archive: bool = False):
        """Return the logged-in shipment list."""
        query = urlencode({"size": limit, "page": page, "archive": str(archive).lower()})
        return await self.request("GET", f"{self.TRACKING_SHIPMENT_URL}/paged?{query}")

    async def get_parcel(self, tracking_uid: str, archive: bool = False):
        """Return details for a specific trackingUid from the shipment list."""
        query = urlencode({"archive": str(archive).lower()})
        encoded = quote(str(tracking_uid), safe="")
        return await self.request("GET", f"{self.TRACKING_SHIPMENT_URL}/details/{encoded}?{query}")

    async def request(
        self,
        method: str,
        url: str,
        *,
        json_data=None,
        ensure_session: bool = True,
    ):
        """Perform a signed myGLS API request."""
        await self._refresh_if_needed()
        if ensure_session:
            await self.ensure_session()

        headers = {
            "Accept": "application/json",
            "Accept-Language": "pl",
            "Content-Type": "application/json",
            "User-Agent": "myGLS/1.6.0-217 (Android 14; Home Assistant) Flutter",
            "Authorization": f"Bearer {self._token}",
            "SessionId": self._session_id,
            **self._signed_headers(method, url),
        }

        async with asyncio.timeout(30):
            async with self._session.request(method, url, headers=headers, json=json_data) as resp:
                text = await resp.text()
                body = _try_json(text)
                if resp.status >= 400:
                    raise Exception(f"GLS API Error: {resp.status} - {text}")
                return body

    async def _refresh_if_needed(self) -> None:
        if self._token and self._expires_at > int(time.time()) + 60:
            return
        await self.refresh_token()

    async def _exchange_code(self, code: str, verifier: str) -> dict:
        return await self._token_request(
            {
                "grant_type": "authorization_code",
                "client_id": self.CLIENT_ID,
                "redirect_uri": self.REDIRECT_URI,
                "code": code,
                "code_verifier": verifier,
                "scope": " ".join(self.ID_SCOPES),
            }
        )

    async def _refresh_oauth_token(self, refresh_token: str, scopes: list[str]) -> dict:
        return await self._token_request(
            {
                "grant_type": "refresh_token",
                "client_id": self.CLIENT_ID,
                "refresh_token": refresh_token,
                "scope": " ".join(scopes),
            }
        )

    async def _token_request(self, data: dict) -> dict:
        url = (
            f"{self.AZURE_BASE_URL}/{self.TENANT}.onmicrosoft.com/oauth2/v2.0/token"
            f"?p={quote(self.SIGN_IN_POLICY)}"
        )
        last_error: Exception | None = None
        for attempt in range(3):
            if attempt:
                await asyncio.sleep(2 * attempt)
            try:
                async with asyncio.timeout(30):
                    async with self._session.post(
                        url,
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                        data=urlencode(data),
                    ) as resp:
                        text = await resp.text()
                        body = _try_json(text)
                        if isinstance(body, dict) and resp.status < 400:
                            return body
                        # 5xx and non-JSON 2xx responses are usually transient
                        # gateway/maintenance pages - retry those.
                        error = Exception(
                            f"GLS token request failed: {resp.status} - {text[:300]!r}"
                        )
                        if resp.status < 500 and isinstance(body, dict):
                            raise error
                        last_error = error
            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                last_error = Exception(f"GLS token request failed: {err}")
        raise last_error

    async def _follow_to_msauth(self, start_url: str, referer: str) -> str:
        url = start_url
        for _ in range(10):
            status, headers, _text = await self._web_request(
                "GET",
                url,
                headers={"Referer": referer},
                allow_redirects=False,
            )
            location = headers.get("Location") or headers.get("location")
            if not location:
                raise Exception(f"GLS login expected redirect, got {status}")
            if location.startswith("msauth://"):
                return location
            url = urljoin(url, location)
        raise Exception("GLS login redirect limit exceeded")

    async def _web_request(
        self,
        method: str,
        url: str,
        *,
        headers: dict | None = None,
        data: str | None = None,
        allow_redirects: bool = False,
    ) -> tuple[int, dict, str]:
        request_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36",
            "Accept-Language": "pl,en;q=0.9",
            **(headers or {}),
        }
        cookie_header = "; ".join(f"{key}={value}" for key, value in self._cookies.items())
        if cookie_header:
            request_headers["Cookie"] = cookie_header

        async with asyncio.timeout(30):
            async with self._session.request(
                method,
                url,
                headers=request_headers,
                data=data,
                allow_redirects=allow_redirects,
            ) as resp:
                for key, cookie in resp.cookies.items():
                    self._cookies[key] = cookie.value
                return resp.status, dict(resp.headers), await resp.text()

    def _authorize_url(self, challenge: str) -> str:
        query = urlencode(
            {
                "state": _random_url_token(24),
                "is_dark": "true",
                "p": self.SIGN_IN_POLICY,
                "prompt": "login",
                "response_type": "code",
                "ui_locales": "pl",
                "nonce": _random_url_token(24),
                "code_challenge_method": "S256",
                "scope": " ".join(self.ID_SCOPES),
                "code_challenge": challenge,
                "redirect_uri": self.REDIRECT_URI,
                "client_id": self.CLIENT_ID,
            }
        )
        return f"{self.AZURE_BASE_URL}/{self.TENANT}.onmicrosoft.com/oauth2/v2.0/authorize?{query}"

    def _signed_headers(self, method: str, url: str) -> dict:
        timestamp = str(int(time.time()))
        nonce = str(uuid.uuid4())
        preimage = "\n".join([method.upper(), url, timestamp, nonce])
        signature = hmac.new(
            self.HMAC_SECRET.encode(),
            preimage.encode(),
            hashlib.sha256,
        ).digest()
        return {
            "X-Api-Key": self.API_KEY,
            "X-Timestamp": timestamp,
            "X-Nonce": nonce,
            "X-Signature": base64.b64encode(signature).decode(),
        }


def _make_pkce() -> tuple[str, str]:
    verifier = _random_url_token(32)
    challenge = _base64_url(hashlib.sha256(verifier.encode()).digest())
    return verifier, challenge


def _random_url_token(size: int = 32) -> str:
    return secrets.token_urlsafe(size)


def _base64_url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _extract_var_json(html: str, name: str) -> dict:
    marker = f"var {name} = "
    start = html.find(marker)
    if start < 0:
        raise Exception(f"GLS login page did not contain {name}")
    start += len(marker)
    end = html.find(";\n", start)
    if end < 0:
        end = html.find(";", start)
    return json.loads(html[start:end])


def _try_json(text: str):
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return text


def _query_param(url: str, name: str) -> str | None:
    from urllib.parse import parse_qs, urlparse

    values = parse_qs(urlparse(url).query).get(name)
    return values[0] if values else None


def _jwt_exp(token: str | None) -> int | None:
    if not token:
        return None
    parts = token.split(".")
    if len(parts) < 2:
        return None
    payload = parts[1] + "=" * (-len(parts[1]) % 4)
    try:
        claims = json.loads(base64.urlsafe_b64decode(payload.encode()).decode())
    except Exception:
        return None
    exp = claims.get("exp")
    return int(exp) if exp else None


