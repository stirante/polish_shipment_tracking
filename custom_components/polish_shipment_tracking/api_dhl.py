import aiohttp
import base64
import hashlib
import json
import urllib.parse
from .api_helpers import normalize_phone, request_json


def _extract_access_token(data: dict) -> str | None:
    """Pull the access JWT out of a DHL auth response.

    Current schema (2026-06): {"token": {"token": "<jwt>", "refresh": ..., "expires": ...}}.
    Older schemas exposed it as `accessToken` either at the top level or nested under `data`.
    The fallbacks keep the integration resilient if DHL flips the shape again.
    """
    if not isinstance(data, dict):
        return None
    token_obj = data.get("token")
    if isinstance(token_obj, dict) and token_obj.get("token"):
        return token_obj["token"]
    return data.get("accessToken") or data.get("data", {}).get("accessToken")


class DhlApi:
    BASE_URL = "https://mojdhl.pl/api/dhl/public"

    def __init__(self, session: aiohttp.ClientSession, device_id: str | None = None):
        self._session = session
        self._token = None
        self._cookies = {}
        self._device_id = device_id

    async def request(self, method: str, path: str, data: dict | None = None):
        url = f"{self.BASE_URL}/{path.lstrip('/')}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "pl-PL",
            "Origin": "https://mojdhl.pl",
        }
        # Add authorization header if token is present
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        # Include any stored cookies in the request
        cookie_header = "; ".join([f"{k}={v}" for k, v in self._cookies.items()])
        if cookie_header:
            headers["Cookie"] = cookie_header

        def _capture_cookies(resp):
            if "Set-Cookie" in resp.headers:
                for cookie in resp.headers.getall("Set-Cookie", []):
                    parts = cookie.split(";", 1)[0].split("=", 1)
                    if len(parts) == 2:
                        self._cookies[parts[0]] = parts[1]

        return await request_json(
            self._session,
            method,
            url,
            json_data=data,
            headers=headers,
            label="DHL",
            log_401_as_info=True,
            error_with_text=True,
            on_response=_capture_cookies,
        )

    async def _solve_altcha(self) -> str:
        """Fetch a fresh Altcha PoW challenge, solve it, return base64-encoded payload.

        DHL gates auth/* endpoints with Altcha (https://altcha.org). Each request needs
        its own single-use solution; reusing a challenge across calls is rejected.
        """
        challenge = await self.request("GET", "auth/captcha/challenge")
        target = challenge["challenge"]
        salt = challenge["salt"]
        algorithm = challenge.get("algorithm", "SHA-256")
        if algorithm != "SHA-256":
            raise Exception(f"DHL Altcha: unsupported algorithm {algorithm}")
        for n in range(challenge["maxnumber"] + 1):
            if hashlib.sha256(f"{salt}{n}".encode()).hexdigest() == target:
                return base64.b64encode(json.dumps({
                    "algorithm": algorithm,
                    "challenge": target,
                    "number": n,
                    "salt": salt,
                    "signature": challenge["signature"],
                }).encode()).decode()
        raise Exception("DHL Altcha: no PoW solution within maxnumber range")

    async def validate_account(self, phone):
        return await self.request(
            "POST",
            "auth/validate-account",
            {
                "phoneNumber": normalize_phone(phone),
                "prefix": "48",
                "captcha-payload": await self._solve_altcha(),
            },
        )

    async def generate_code(self, phone):
        return await self.request(
            "POST",
            "auth/generate-code",
            {
                "phoneNumber": normalize_phone(phone),
                "prefix": "48",
                "isMobileDevice": False,
                "captcha-payload": await self._solve_altcha(),
            },
        )

    async def validate_code(self, phone, code, device_id):
        data = await self.request(
            "POST",
            "auth/validate-code",
            {
                "phoneNumber": normalize_phone(phone),
                "prefix": "48",
                "smsCode": code,
                "deviceId": device_id,
                "deviceName": "HomeAssistant",
                "rememberMe": True,
                "captcha-payload": await self._solve_altcha(),
            },
        )
        self._token = _extract_access_token(data)
        return data

    async def refresh_token(self):
        """Refresh the DHL token using the auth/recover endpoint."""
        if not self._device_id:
            raise Exception("Device ID required for DHL refresh")

        payload = {
            "deviceName": "HomeAssistant",
            "deviceId": self._device_id,
        }

        if self._token:
            self._cookies["access-token"] = self._token

        data = await self.request("POST", "auth/recover", data=payload)

        new_token = _extract_access_token(data)
        if new_token:
            self._token = new_token
        return data

    async def get_parcels(self):
        return await self.request(
            "POST",
            "user/shipment/v2.1/list/incoming/active/1",
            {
                "shipmentFilterTypes": [],
                "shipmentFilterStatuses": [],
                "page": 1,
            },
        )

    async def get_parcel(self, shipment_number: str):
        encoded = urllib.parse.quote(str(shipment_number), safe="")
        return await self.request("GET", f"user/shipment/v2/details/{encoded}")
