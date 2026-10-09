import logging
import urllib.parse
from datetime import datetime, timezone, timedelta
import aiohttp
from .api_helpers import normalize_phone, request_json

_LOGGER = logging.getLogger(__name__)

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

    async def get_parcel(self, shipment_number: str):
        encoded = urllib.parse.quote(str(shipment_number), safe="")
        return await self.request("GET", f"v4/parcels/tracked/{encoded}")
        
    async def get_parcels(self):
        """Pobiera paczki z ostatnich dni za pomocą właściwego parametru updatedAfter."""
        now = datetime.now(timezone.utc)
        
        # Pobieramy zdarzenia z ostatnich 7 dni!
        start_date = now - timedelta(days=7)
        cursor = start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        all_parcels = []
        has_more = True
        max_pages = 5  # Przy oknie 7 dni zazwyczaj wystarcza 1 zapytanie

        while has_more and max_pages > 0:
            max_pages -= 1
            path = f"v4/parcels/tracked?updatedAfter={cursor}"

            data = await self.request("GET", path)
            if not data or not isinstance(data, dict):
                break

            batch = data.get("parcels", [])
            all_parcels.extend(batch)
            has_more = data.get("more", False)
            cursor = data.get("updatedUntil")

            if not cursor or not batch:
                break

        # Deduplikacja
        unique_parcels = {p.get("shipmentNumber"): p for p in all_parcels if p.get("shipmentNumber")}
        active_parcels = []

        for p in unique_parcels.values():
            status = p.get("status", "")
            status_group = p.get("statusGroup", "")
            open_code = p.get("openCode")
            pickup_date = p.get("pickUpDate")

            # 1. Paczka oczekująca w Paczkomacie (posiada kod odbioru, nieodebrana)
            if open_code and not pickup_date:
                active_parcels.append(p)
                continue

            # 2. Paczki w doręczeniu / transporcie
            if (
                status in ("READY_TO_PICKUP", "OUT_FOR_DELIVERY", "STACKED", "AVIZO")
                or status_group in ("READY_TO_PICKUP", "OUT_FOR_DELIVERY")
            ):
                active_parcels.append(p)
                continue

            # 3. Ignoruj martwe etykiety utworzone ponad 5 dni temu
            if status == "CONFIRMED":
                events = p.get("eventLog", [])
                date_str = events[0].get("date") if events else p.get("storedDate")
                if date_str:
                    try:
                        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        if now - dt > timedelta(days=5):
                            continue
                    except Exception:
                        pass
                active_parcels.append(p)
                continue

            # 4. Ignoruj odebrane paczki starsze niż 24h
            if status == "DELIVERED" or status_group == "DELIVERED":
                if pickup_date:
                    try:
                        p_dt = datetime.fromisoformat(pickup_date.replace("Z", "+00:00"))
                        if now - p_dt > timedelta(hours=24):
                            continue
                    except Exception:
                        pass
                else:
                    continue

            active_parcels.append(p)

        _LOGGER.info(
            "InPost: Pobrano %d bieżących paczek, wyselekcjonowano %d aktywnych",
            len(unique_parcels),
            len(active_parcels),
        )
        return {"parcels": active_parcels}
