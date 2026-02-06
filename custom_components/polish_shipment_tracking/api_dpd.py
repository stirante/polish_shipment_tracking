import aiohttp
import logging
import time
import urllib.parse

from .api_helpers import normalize_phone, request_json

_LOGGER = logging.getLogger(__name__)


class DpdApi:
    SSO_URL = "https://dpdsso.dpd.com.pl"
    API_URL = "https://mobapp.dpd.com.pl"
    CLIENT_ID = "DPDClientMDU"

    def __init__(self, session: aiohttp.ClientSession):
        self._session = session
        self._token = None
        self._refresh_token = None
        self._expires_at = 0

    async def request(self, method, url, data=None, headers=None, form_data=None):
        if headers is None:
            headers = {}

        # Refresh access token if it is about to expire
        if self._token and self._refresh_token and time.time() > self._expires_at - 60:
            await self.refresh_access_token()

        default_headers = {
            "Accept": "application/json",
            "User-Agent": "DPD Mobile",
        }
        if self._token:
            default_headers["Authorization"] = f"Bearer {self._token}"
        headers = {**default_headers, **headers}

        kwargs = {"headers": headers}
        if data:
            kwargs["json"] = data
        if form_data:
            kwargs["data"] = form_data

        return await request_json(
            self._session,
            method,
            url,
            json_data=data if data else None,
            data=form_data if form_data else None,
            headers=headers,
            label="DPD",
            log_401_as_info=True,
            error_with_text=False,
        )

    async def send_sms_code(self, phone_number):
        phone = normalize_phone(phone_number)
        url = f"{self.SSO_URL}/api/phone-verifications/{phone}"
        await self.request("PUT", url)
        return True

    async def register_with_code(self, phone_number, code):
        phone = normalize_phone(phone_number)
        url = f"{self.SSO_URL}/api/users"
        params = {
            "redirect_uri": "https://dpdsso.dpd.com.pl/landing-page?messageType=activeAccount",
            "client_id": self.CLIENT_ID,
        }
        url_with_params = f"{url}?{urllib.parse.urlencode(params)}"

        payload = {
            "emailRegistration": None,
            "phoneRegistration": {"phone": phone, "code": code},
            "type": "PhoneBasedUserRegistrationModel",
        }

        resp = await self.request("POST", url_with_params, data=payload)
        auth_code = resp.get("code")

        token_url = f"{self.SSO_URL}/auth/realms/DPD/protocol/openid-connect/token"
        form_data = {
            "code": auth_code,
            "grant_type": "authorization_code",
            "client_id": self.CLIENT_ID,
        }
        token_data = await self.request("POST", token_url, form_data=form_data)
        self._save_token_data(token_data)
        return token_data

    async def refresh_access_token(self):
        if not self._refresh_token:
            raise Exception("Missing DPD refresh token")

        url = f"{self.SSO_URL}/auth/realms/DPD/protocol/openid-connect/token"
        form_data = {
            "refresh_token": self._refresh_token,
            "grant_type": "refresh_token",
            "client_id": self.CLIENT_ID,
        }
        try:
            async with self._session.post(url, data=form_data) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"DPD refresh failed: {resp.status} {text}")
                data = await resp.json()
                if not data.get("access_token"):
                    raise Exception("DPD refresh failed: missing access_token")
                self._save_token_data(data)
        except Exception as e:
            _LOGGER.error("DPD Token refresh failed: %s", e)
            raise

    def _save_token_data(self, data):
        self._token = data.get("access_token")
        if data.get("refresh_token"):
            self._refresh_token = data.get("refresh_token")
        expires_in = data.get("expires_in", 300)
        self._expires_at = time.time() + expires_in

    async def get_parcels(self):
        url = f"{self.API_URL}/mdupackageservices/api/v1/packages?userContext=RECEIVER"
        headers = {
            "X-Mobile-Platform": "android",
            "X-Mobile-Version": "2.10.2",
        }
        payload = {"alias": None, "sent": None}
        return await self.request("POST", url, data=payload, headers=headers)
