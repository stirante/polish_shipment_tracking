import aiohttp
import urllib.parse
from .api_helpers import normalize_phone, request_json


class InPostApi:
    BASE_URL = "https://api-inmobile-pl.easypack24.net"

    def __init__(self, session: aiohttp.ClientSession, device_uid: str | None = None):
        self._session = session
        self._token = None
        self._refresh_token = None
        self._device_uid = device_uid

    async def request(self, method, path, data=None, headers=None):
        if headers is None:
            headers = {}

        url = f"{self.BASE_URL}/{path.lstrip('/')}"
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "InPost-Mobile",
            "Accept": "application/json",
        }

        if self._device_uid:
            default_headers["device-uid"] = self._device_uid
        if self._token:
            default_headers["Authorization"] = f"Bearer {self._token}"

        headers = {**default_headers, **headers}

        return await request_json(
            self._session,
            method,
            url,
            json_data=data,
            headers=headers,
            label="InPost",
            log_401_as_info=True,
            error_with_text=True,
        )

    async def send_sms_code(self, phone_number):
        phone = normalize_phone(phone_number)
        payload = {
            "phoneNumber": {
                "value": str(phone),
                "prefix": "+48",
            }
        }
        return await self.request("POST", "/v1/account", payload)

    async def confirm_sms_code(self, phone_number, code):
        phone = normalize_phone(phone_number)
        payload = {
            "phoneNumber": {
                "value": str(phone),
                "prefix": "+48",
            },
            "smsCode": str(code),
            "devicePlatform": "Android",
        }
        data = await self.request("POST", "/v1/account/verification", payload)
        self._token = data.get("authToken")
        self._refresh_token = data.get("refreshToken")
        return data

    async def refresh_token(self):
        """Refresh the InPost token."""
        if not self._refresh_token:
            raise Exception("Missing InPost refresh token")

        payload = {
            "refreshToken": self._refresh_token,
            "phoneOS": "Android",
        }

        data = await self.request("POST", "v1/authenticate", payload)

        new_auth = data.get("authToken")
        if new_auth:
            self._token = new_auth
            if data.get("refreshToken"):
                self._refresh_token = data.get("refreshToken")

        return data

    async def get_parcels(self):
        return await self.request("GET", "v4/parcels/tracked")

    async def get_parcel(self, shipment_number: str):
        encoded = urllib.parse.quote(str(shipment_number), safe="")
        return await self.request("GET", f"v4/parcels/tracked/{encoded}")
