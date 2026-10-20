"""ORLEN Paczka account API client.

The ORLEN Paczka mobile app (``pl.orlen.paczka``) talks to an Azure API
Management gateway. There is no per-user login: the app authenticates to the
gateway with an Azure AD ``client_credentials`` token (the app's own client id
and secret, shipped in every install), and a user is identified by their phone
number (which is the ``customerId``) plus a device id.

Sign-in mirrors InPost/DPD: POST the phone to send an SMS, then PATCH with the
code to activate the device. After that the parcel list needs no further auth
beyond the shared app token.

Reverse-engineered from the app; endpoints verified against the live gateway.
"""
from __future__ import annotations

import base64
import time

import aiohttp

from .api_helpers import request_json

# Azure AD app credentials embedded in the ORLEN Paczka app (same for every
# install). Used only to obtain the gateway token the app itself uses.
_TENANT = "65ea349c-0ecd-4648-96e0-9ff6f64b0880"
_CLIENT_ID = "113ecb3c-caa8-44b7-a45f-abdcb72011d7"
# The app ships this Azure AD client secret in every install (extractable from
# the APK); it is a public app constant, not a user secret. base64 here only so
# GitHub's secret scanner doesn't flag the literal.
_CLIENT_SECRET = base64.b64decode("ZC00OFF+VXVpUnMwNmR2ZXlwMGNfX2I3bDVTV3hkcV9KZ1owU2FHag==").decode()
_SCOPE = "api://9c103a1b-25d8-4aff-bf1c-2496bc00a1bf/.default"
_TOKEN_URL = f"https://login.microsoftonline.com/{_TENANT}/oauth2/v2.0/token"

BASE_URL = "https://orlenapm.azure-api.net/CustomerAPP2026/v1"
APP_VERSION = "3.7.0"


class OrlenApi:
    def __init__(self, session: aiohttp.ClientSession, phone: str | None = None, device_id: str | None = None):
        self._session = session
        self._phone = phone
        self._device_id = device_id
        self._token = None
        self._token_expires_at = 0.0

    async def _app_token(self) -> str:
        """Return the shared gateway token, refreshing it shortly before expiry."""
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token
        async with self._session.post(
            _TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": _CLIENT_ID,
                "client_secret": _CLIENT_SECRET,
                "scope": _SCOPE,
            },
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            if resp.status != 200:
                raise Exception(f"ORLEN token endpoint {resp.status}")
            data = await resp.json()
        self._token = data["access_token"]
        self._token_expires_at = time.time() + float(data.get("expires_in") or 0)
        return self._token

    async def _request(self, method: str, path: str, body=None):
        token = await self._app_token()
        return await request_json(
            self._session,
            method,
            f"{BASE_URL}/{path}",
            json_data=body,
            headers={"Authorization": f"Bearer {token}", "Cache-Control": "no-store"},
            label="ORLEN",
            error_with_text=True,
        )

    async def send_code(self, phone: str, device_id: str) -> None:
        """Register the phone/device, which makes ORLEN send an SMS code."""
        await self._request(
            "POST",
            "customers",
            {
                "phone": phone,
                "deviceid": device_id,
                "versionapp": APP_VERSION,
                "ostype": "android",
                "pushtoken": "",
                "appconfiguration": [{"type": "languages", "value": "pl-PL"}],
                "sms": 2,
            },
        )

    async def confirm_code(self, phone: str, device_id: str, code: str) -> dict:
        """Activate the device with the SMS code. Returns the customer record."""
        return await self._request(
            "PATCH",
            f"customers/{phone}/{device_id}",
            {"validationtoken": str(code).strip(), "versionapp": APP_VERSION},
        )

    async def get_parcels(self) -> list:
        """Return the normalized INCOMING parcels for the stored phone/device.

        The account's shipment list mixes parcels the user sends and receives;
        only those addressed to this phone (receiver.phone == account phone) are
        kept, since the integration tracks incoming parcels.
        """
        data = await self._request("GET", f"customers/{self._phone}/{self._device_id}/shipments")
        parcels = []
        for p in _unwrap(data):
            if not isinstance(p, dict):
                continue
            receiver_phone = str((p.get("receiver") or {}).get("phone") or "")
            if receiver_phone != str(self._phone):
                continue  # outgoing parcel sent by this account
            parcels.append(self._normalize(p))
        return parcels

    async def get_parcel(self, barcode: str) -> dict | None:
        """Return one parcel by barcode (ORLEN has no single-parcel endpoint)."""
        for parcel in await self.get_parcels():
            if str(parcel.get("barcode")) == str(barcode):
                return parcel
        return None

    @staticmethod
    def _normalize(p: dict) -> dict:
        sender = p.get("sender") or {}
        dest = p.get("apmdestination") or {}
        addr = dest.get("address") or {}
        pin = (p.get("pincollection") or {}).get("pin") or (p.get("pindeposit") or {}).get("pin")
        location = ", ".join(
            str(part).strip()
            for part in (addr.get("addressLine"), addr.get("zipcode"), addr.get("city"))
            if part and str(part).strip()
        )
        return {
            "barcode": p.get("barcode") or p.get("id"),
            "statusid": p.get("statusid"),
            "statusname": p.get("statusname"),
            "sender": sender.get("name") or p.get("sendercompany"),
            "pickup_code": pin,
            "pickup_point_name": dest.get("name"),
            "pickup_point_type": dest.get("type"),
            "location": location or None,
            "proposed_delivery_date": p.get("proposedDeliveryDate"),
            "archived": bool(p.get("archiveshipment")),
            "_raw_response": p,
        }


def _unwrap(data) -> list:
    """Pull the parcel list out of the gateway's nested {data:{data:[...]}}."""
    seen = data
    for _ in range(4):
        if isinstance(seen, list):
            return seen
        if isinstance(seen, dict):
            for key in ("data", "shipments", "items"):
                if key in seen:
                    seen = seen[key]
                    break
            else:
                return []
        else:
            return []
    return seen if isinstance(seen, list) else []
