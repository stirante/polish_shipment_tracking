import aiohttp
import urllib.parse
from .api_helpers import normalize_phone, request_json


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

    async def validate_account(self, phone):
        return await self.request(
            "POST",
            "auth/validate-account",
            {"phoneNumber": normalize_phone(phone), "prefix": "48", "captcha-payload": " "},
        )

    async def generate_code(self, phone, captcha_payload=" "):
        return await self.request(
            "POST",
            "auth/generate-code",
            {
                "phoneNumber": normalize_phone(phone),
                "prefix": "48",
                "isMobileDevice": False,
                "captcha-payload": captcha_payload,
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
                "captcha-payload": " ",
            },
        )
        self._token = data.get("accessToken") or data.get("data", {}).get("accessToken")
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

        new_token = data.get("accessToken") or data.get("data", {}).get("accessToken")
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
