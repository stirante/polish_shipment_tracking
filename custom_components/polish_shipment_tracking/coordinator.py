from datetime import datetime, timezone, timedelta
import asyncio
import logging
import json
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
import aiohttp

from homeassistant.helpers.dispatcher import async_dispatcher_connect, async_dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import (
    async_create_clientsession,
    async_get_clientsession,
)

from .const import (
    DOMAIN,
    CONF_TOKEN,
    CONF_REFRESH_TOKEN,
    CONF_TOKEN_EXPIRES_AT,
    CONF_REFRESH_EXPIRES_AT,
    CONF_COURIER,
    CONF_DEVICE_UID,
    CONF_PHONE,
    CONF_ID_TOKEN,
    CONF_SESSION_ID,
    CONF_SESSION_REGISTERED,
    CONF_COOKIE,
    CONF_INCLUDE_RECIPIENTS,
    CONF_EXCLUDE_RECIPIENTS,
    CONF_HIDDEN_SHIPMENTS,
    SIGNAL_PARCELS_UPDATED,
    SIGNAL_ALLEGRO_ORDERS_UPDATED,
)
from .api_inpost import InPostAuthError
from .helpers import (
    get_parcel_detail_id,
    get_parcel_id,
    get_parcel_tracking_numbers,
    add_hidden_shipment,
    get_raw_status,
    is_delivered,
    is_hidden_shipment,
    matches_recipient_filters,
    merge_allegro_details,
    normalize_allegro_orders,
    normalize_status,
    parse_hidden_shipments,
    parse_recipient_patterns,
    reconcile_departed_parcels,
)

_LOGGER = logging.getLogger(__name__)

DEAD_LABEL_THRESHOLD = timedelta(days=7)


def _parse_datetime_safe(val: Any) -> datetime | None:
    """Parse various datetime string/timestamp formats into timezone-aware UTC datetime."""
    if not val:
        return None
    if isinstance(val, (int, float)):
        ts = val / 1000.0 if val > 1e11 else float(val)
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    if isinstance(val, datetime):
        return val if val.tzinfo is not None else val.replace(tzinfo=timezone.utc)
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return None
        clean_val = val[:-1] + "+00:00" if val.endswith("Z") else val
        try:
            dt = datetime.fromisoformat(clean_val)
            return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            pass
        try:
            from homeassistant.util.dt import parse_datetime
            dt = parse_datetime(val)
            if dt is not None:
                return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
        except Exception:
            pass
    return None


def _has_courier_movement(parcel: dict, courier: str) -> bool:
    """Check if parcel history contains courier movement beyond creation."""
    events = parcel.get("eventLog") or parcel.get("events") or []
    if not isinstance(events, list):
        return False
    for event in events:
        if not isinstance(event, dict):
            continue
        event_name = (
            event.get("name")
            or event.get("status")
            or event.get("eventTitle")
            or event.get("state")
        )
        if event_name:
            key = normalize_status(str(event_name), courier)
            if key not in {"created", "unknown"}:
                return True
    return False


def _get_stale_label_date(parcel: dict) -> datetime | None:
    """Get the label generation date or last eventLog entry date."""
    events = parcel.get("eventLog") or parcel.get("events") or []
    latest_event_date = None
    if isinstance(events, list) and events:
        for event in events:
            if isinstance(event, dict):
                date_val = (
                    event.get("date")
                    or event.get("datetime")
                    or event.get("timestamp")
                    or event.get("eventDate")
                )
                dt = _parse_datetime_safe(date_val)
                if dt is not None and (latest_event_date is None or dt > latest_event_date):
                    latest_event_date = dt

    if latest_event_date is not None:
        return latest_event_date

    for field in (
        "creationDate",
        "createdDate",
        "createdAt",
        "created_at",
        "shipmentDate",
        "updatedDate",
        "updatedAt",
    ):
        val = parcel.get(field)
        dt = _parse_datetime_safe(val)
        if dt is not None:
            return dt

    return None


def is_dead_label(parcel: dict, courier: str, threshold: timedelta = DEAD_LABEL_THRESHOLD) -> bool:
    """Check if parcel is a stale/dead label (CONFIRMED/CREATED) without courier movement."""
    # Only InPost keeps labels that were never sent on the tracked list.
    if courier != "inpost":
        return False
    raw_status = str(get_raw_status(parcel, courier) or "").strip().upper()
    status_key = normalize_status(raw_status, courier)

    if raw_status not in {"CONFIRMED", "CREATED", "OFFER_SELECTED", "OFFERS_PREPARED"} and status_key != "created":
        return False

    if _has_courier_movement(parcel, courier):
        return False

    label_date = _get_stale_label_date(parcel)
    if label_date is None:
        return False

    now = datetime.now(timezone.utc)
    return (now - label_date) > threshold

class ShipmentCoordinator(DataUpdateCoordinator):
    """Class to manage fetching shipment data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the coordinator."""
        self.entry = entry
        self.courier = entry.data[CONF_COURIER]
        self.known_parcels = set()
        self.pending_lifecycle_events: list[tuple[str, dict]] = []
        self._missing_parcel_counts: dict[str, int] = {}
        self.add_entities_callback = None
        # Per-account session owned by this coordinator (DHL/GLS). Their auth is
        # cookie-based, so accounts must NOT share HA's global cookie jar or one
        # account's access-token cookie bleeds into the other's requests.
        self._owned_session: aiohttp.ClientSession | None = None
        self._include_recipients = parse_recipient_patterns(
            entry.options.get(CONF_INCLUDE_RECIPIENTS)
        )
        self._exclude_recipients = parse_recipient_patterns(
            entry.options.get(CONF_EXCLUDE_RECIPIENTS)
        )
        self._hidden_shipments = parse_hidden_shipments(
            entry.options.get(CONF_HIDDEN_SHIPMENTS)
        )
        # Every number the hidden parcels are known under, so Allegro does
        # not show them again as its own orders.
        self.hidden_tracking_numbers: set[str] = set(self._hidden_shipments)
        # Allegro only: every order from the last fetch, including the ones
        # hidden because a carrier account already tracks the same parcel.
        self.allegro_orders: list[dict] = []

        super().__init__(
            hass,
            _LOGGER,
            name=f"Shipment Tracking {self.courier}",
            update_interval=timedelta(minutes=15),
        )

        self.session = async_get_clientsession(hass)
        self.api = self._get_api_instance()

    @callback
    def async_start_linking(self):
        """Wire the cross-account parcel matching; returns the unsubscribe callback."""
        if self.courier == "allegro":
            remove_signal = async_dispatcher_connect(
                self.hass, SIGNAL_PARCELS_UPDATED, self._async_carrier_parcels_updated
            )
            remove_listener = self.async_add_listener(self._async_announce_orders)

            @callback
            def _remove():
                remove_signal()
                remove_listener()

            return _remove
        remove_listener = self.async_add_listener(self._async_announce_parcels)
        # The first refresh ran before this listener existed; announce it so an
        # Allegro account that started earlier can hide its duplicates now.
        self._async_announce_parcels()
        return remove_listener

    @callback
    def _async_announce_orders(self) -> None:
        async_dispatcher_send(self.hass, SIGNAL_ALLEGRO_ORDERS_UPDATED)

    @callback
    def _async_announce_parcels(self) -> None:
        async_dispatcher_send(self.hass, SIGNAL_PARCELS_UPDATED)

    @callback
    def _async_carrier_parcels_updated(self) -> None:
        """Re-hide Allegro orders once a carrier account picks the parcel up."""
        if self.data is None:
            return
        visible = self._filter_active_parcels(self.allegro_orders)
        if visible != self.data:
            # Set data directly: async_set_updated_data would reschedule the
            # poll, and frequent carrier updates could then starve it.
            self.data = visible
            self.async_update_listeners()

    def _carrier_tracking_numbers(self) -> set[str]:
        """Tracking numbers held by the carrier accounts since startup.

        Remembered after the carrier drops a parcel too: carriers usually
        report the pickup before Allegro does, and the order must not pop
        back up as a new Allegro shipment in between. Parcels the user hid
        in a carrier account count too, so they stay hidden in Allegro.
        """
        domain_data = self.hass.data.setdefault(DOMAIN, {})
        numbers: set[str] = domain_data.setdefault("_carrier_tracking_numbers", set())
        for coordinator in domain_data.values():
            if not isinstance(coordinator, ShipmentCoordinator) or coordinator.courier == "allegro":
                continue
            numbers |= coordinator.hidden_tracking_numbers
            for parcel in coordinator.data or []:
                numbers |= get_parcel_tracking_numbers(parcel, coordinator.courier)
        return numbers

    def _get_api_instance(self):
        """Get API instance based on courier."""
        data = self.entry.data
        token = data.get(CONF_TOKEN)
        refresh_token = data.get(CONF_REFRESH_TOKEN)
        device_uid = data.get(CONF_DEVICE_UID)
        
        if self.courier == "inpost":
            from .api_inpost import InPostApi
            api = InPostApi(self.session, device_uid=device_uid)
            api._token = token
            api._refresh_token = refresh_token
            # Entries from before the OAuth login have no expiry: the first
            # request refreshes, InPost rejects the old token and HA asks to
            # sign in again.
            api._expires_at = data.get(CONF_TOKEN_EXPIRES_AT, 0) or 0
            return api
            
        elif self.courier == "dpd":
            from .api_dpd import DpdApi
            api = DpdApi(self.session)
            api._token = token
            api._refresh_token = refresh_token
            api._expires_at = data.get(CONF_TOKEN_EXPIRES_AT, 0) or 0
            return api
            
        elif self.courier == "dhl":
            from .api_dhl import DhlApi
            # Isolated session with a dummy cookie jar so this account's DHL
            # cookies never leak into (or get overwritten by) another account
            # sharing HA's global session. Cookies are carried explicitly by
            # DhlApi via the Cookie header / self._cookies instead.
            self._owned_session = async_create_clientsession(
                self.hass, cookie_jar=aiohttp.DummyCookieJar()
            )
            api = DhlApi(self._owned_session, device_id=device_uid)
            api._token = token

            cookies_json = data.get("cookies")
            if cookies_json:
                try:
                    api._cookies = json.loads(cookies_json)
                except Exception as e:
                    _LOGGER.warning("Failed to restore DHL cookies: %s", e)
            
            return api

        elif self.courier == "pocztex":
            from .api_pocztex import PocztexApi
            api = PocztexApi(self.session)
            api._token = token
            api._refresh_token = refresh_token
            api._expires_at = data.get(CONF_TOKEN_EXPIRES_AT, 0) or 0
            api._refresh_expires_at = data.get(CONF_REFRESH_EXPIRES_AT, 0) or 0
            return api

        elif self.courier == "gls":
            from .api_gls import GlsApi
            # GlsApi manages cookies manually; a shared session's cookie jar
            # accumulates Azure B2C cookies that eventually poison token
            # requests, so give it a cookieless session (same as config flow).
            self._owned_session = async_create_clientsession(
                self.hass, cookie_jar=aiohttp.DummyCookieJar()
            )
            api = GlsApi(self._owned_session, session_id=data.get(CONF_SESSION_ID))
            api._token = token
            api._refresh_token = refresh_token
            api._id_token = data.get(CONF_ID_TOKEN)
            api._expires_at = data.get(CONF_TOKEN_EXPIRES_AT, 0) or 0
            api._session_registered = data.get(CONF_SESSION_REGISTERED)
            return api

        elif self.courier == "allegro":
            from .api_allegro import AllegroApi
            return AllegroApi(self.session, data.get(CONF_COOKIE))

        elif self.courier == "orlen":
            from .api_orlen import OrlenApi
            return OrlenApi(self.session, phone=data.get(CONF_PHONE), device_id=device_uid)
        return None

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            parcels = await self._fetch_parcels_with_retry()
            self._persist_auth_if_changed()
            events, retained, missing_counts = reconcile_departed_parcels(
                self.data, parcels, self.courier, self._missing_parcel_counts
            )
            self.pending_lifecycle_events = events
            self._missing_parcel_counts = missing_counts
            return self._filter_active_parcels(parcels) + retained
        except InPostAuthError as err:
            # The refresh token was rejected: HA shows a repair notification
            # and a reauth flow with a new sign-in link.
            raise ConfigEntryAuthFailed(
                "InPost session expired, sign in again"
            ) from err
        except Exception as err:
            if self.courier == "allegro" and any(code in str(err) for code in ("401", "403")):
                # The pasted session cookie expired: let HA ask for a new one
                # (repair notification + reauth flow) instead of failing silently.
                raise ConfigEntryAuthFailed(
                    "Allegro session expired, paste a new QXLSESSID cookie"
                ) from err
            _LOGGER.error("Error fetching data for %s: %s", self.courier, err)
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def _fetch_parcels_with_retry(self):
        """Fetch parcels and retry once if unauthorized."""
        try:
            return await self._fetch_parcels()
        except InPostAuthError:
            raise
        except Exception as e:
            if "401" in str(e) or "unauthorized" in str(e).lower():
                _LOGGER.info("%s token expired, refreshing...", self.courier)
                await self._refresh_token()
                return await self._fetch_parcels()
            raise e

    async def _fetch_single_parcel_with_retry(self, tracking_number: str):
        """Fetch one parcel and retry once if unauthorized."""
        try:
            return await self._fetch_single_parcel(tracking_number)
        except InPostAuthError:
            raise
        except Exception as e:
            if "401" in str(e) or "unauthorized" in str(e).lower():
                _LOGGER.info("%s token expired while fetching single parcel, refreshing...", self.courier)
                await self._refresh_token()
                return await self._fetch_single_parcel(tracking_number)
            raise e

    async def _fetch_parcels(self):
        """Fetch parcels from API without retry logic."""
        if self.courier == "inpost":
            data = await self.api.get_parcels()
            return data if isinstance(data, list) else data.get("parcels", [])
            
        elif self.courier == "dpd":
            data = await self.api.get_parcels()
            parcels = []
            if isinstance(data, list):
                parcels = data
            elif isinstance(data, dict):
                if "packages" in data:
                    parcels = data["packages"]
                elif "parcelList" in data:
                    parcels = data["parcelList"]
                elif "shipments" in data:
                    parcels = data["shipments"]
            if not parcels:
                return []
            return await self._enrich_parcels_with_details(parcels)
            
        elif self.courier == "dhl":
            data = await self.api.get_parcels()
            parcels = data.get("shipments", []) if isinstance(data, dict) else []
            if not parcels:
                return []
            # The list payload has no events and no pickup point, so the card
            # would show an almost empty dialog without the details call.
            return await self._enrich_parcels_with_details(parcels)

        elif self.courier == "pocztex":
            data = await self.api.get_parcels()
            parcels = []
            if isinstance(data, list):
                parcels = data
            elif isinstance(data, dict):
                for key in ("packages", "items", "tracking", "data", "content"):
                    if key in data and isinstance(data[key], list):
                        parcels = data[key]
                        break
            # Keep archive markers for lifecycle classification, but do not
            # request details for parcels that are already archived.
            if not parcels:
                return []

            # Pocztex needs separate calls for details
            detail_tasks = []
            for parcel in parcels:
                detail_id = None
                if isinstance(parcel, dict) and parcel.get("archived") is not True:
                    detail_id = get_parcel_detail_id(parcel, self.courier)
                if detail_id is None:
                    detail_tasks.append(asyncio.sleep(0, result=None))
                else:
                    detail_tasks.append(self.api.get_parcel_details(detail_id))

            details_results = await asyncio.gather(*detail_tasks, return_exceptions=True)
            enriched = []
            for parcel, details in zip(parcels, details_results):
                if isinstance(details, Exception) or details is None:
                    enriched.append(parcel)
                    continue

                if isinstance(parcel, dict):
                    merged = dict(parcel)
                    if isinstance(details, dict):
                        merged.update(details)
                    merged["_raw_response"] = details
                    enriched.append(merged)
                else:
                    enriched.append(parcel)
            return enriched

        elif self.courier == "gls":
            data = await self.api.get_parcels()
            self._persist_auth_if_changed()
            parcels = []
            if isinstance(data, list):
                parcels = data
            elif isinstance(data, dict):
                for key in ("items", "shipments", "data", "content", "packages", "parcels"):
                    if isinstance(data.get(key), list):
                        parcels = data[key]
                        break
            if not parcels:
                return []

            detail_tasks = []
            for parcel in parcels:
                tracking_uid = parcel.get("trackingUid") if isinstance(parcel, dict) else None
                if tracking_uid is None:
                    detail_tasks.append(asyncio.sleep(0, result=None))
                else:
                    detail_tasks.append(self.api.get_parcel(tracking_uid))

            details_results = await asyncio.gather(*detail_tasks, return_exceptions=True)
            self._persist_auth_if_changed()
            enriched = []
            for parcel, details in zip(parcels, details_results):
                if isinstance(details, Exception):
                    uid = parcel.get("trackingUid") if isinstance(parcel, dict) else None
                    _LOGGER.debug("GLS detail fetch failed for %s: %s", uid, details)
                    enriched.append(parcel)
                    continue
                if details is None:
                    enriched.append(parcel)
                    continue
                if not isinstance(parcel, dict) or not isinstance(details, dict):
                    enriched.append(parcel)
                    continue
                merged = dict(parcel)
                tracking_shipment = details.get("trackingShipment")
                if isinstance(tracking_shipment, dict):
                    merged.update(tracking_shipment)
                merged.update(details)
                merged["_raw_response"] = details
                enriched.append(merged)
            return enriched

        elif self.courier == "allegro":
            data = await self.api.get_orders()
            if not isinstance(data, dict):
                raise Exception(f"Allegro API Error: unexpected orders response: {str(data)[:200]}")
            orders = normalize_allegro_orders(data)
            # Recipient data (for the filters) and the timeline only come with
            # the per-order details, so fetch them for orders still under way.
            semaphore = asyncio.Semaphore(5)

            async def _with_details(order):
                if is_delivered(order, self.courier):
                    return order
                try:
                    async with semaphore:
                        details = await self.api.get_order(order["orderId"])
                except Exception as err:
                    # Without details the recipient filters cannot see who the
                    # parcel is for, so this is worth surfacing.
                    _LOGGER.warning("Allegro order details failed for %s: %s", order["orderId"], err)
                    return order
                return merge_allegro_details(order, details)

            self.allegro_orders = list(await asyncio.gather(*(_with_details(order) for order in orders)))
            return self.allegro_orders

        elif self.courier == "orlen":
            return await self.api.get_parcels()

        return []

    async def _enrich_parcels_with_details(self, parcels):
        """Fetch per-parcel details to expose fields missing from the list endpoint."""
        semaphore = asyncio.Semaphore(5)

        async def _fetch_details(parcel):
            if not isinstance(parcel, dict):
                return parcel

            tracking_number = get_parcel_id(parcel, self.courier)
            if not tracking_number:
                return parcel

            try:
                async with semaphore:
                    details = await self.api.get_parcel(tracking_number)
            except Exception as err:
                _LOGGER.debug(
                    "Failed to fetch %s parcel details for %s, keeping list payload: %s",
                    self.courier,
                    tracking_number,
                    err,
                )
                return parcel

            detail_parcel = self._extract_single_parcel(details, tracking_number)
            if not isinstance(detail_parcel, dict):
                return parcel

            merged = dict(parcel)
            merged.update(detail_parcel)
            merged["_raw_response"] = detail_parcel
            return merged

        details_results = await asyncio.gather(
            *(_fetch_details(parcel) for parcel in parcels),
            return_exceptions=True,
        )

        enriched = []
        for parcel, result in zip(parcels, details_results):
            if isinstance(result, Exception):
                enriched.append(parcel)
            else:
                enriched.append(result)
        return enriched

    async def async_close(self) -> None:
        """Close any session owned by this coordinator (DHL/GLS isolated session)."""
        if self._owned_session is not None:
            await self._owned_session.close()
            self._owned_session = None

    def _get_gls_tracking_uid(self, shipment_no: str) -> str | None:
        """Return the trackingUid for a GLS shipment identified by shipmentNo."""
        for parcel in (self.data or []):
            if not isinstance(parcel, dict):
                continue
            ts = parcel.get("trackingShipment")
            candidates = [parcel, ts] if isinstance(ts, dict) else [parcel]
            for candidate in candidates:
                if str(candidate.get("shipmentNo") or "") == str(shipment_no):
                    uid = candidate.get("trackingUid")
                    if uid:
                        return str(uid)
        return None

    async def _fetch_single_parcel(self, tracking_number: str):
        """Fetch a single parcel details for couriers that support it."""
        if self.courier == "orlen":
            return await self.api.get_parcel(tracking_number)

        if self.courier in {"inpost", "dpd", "dhl", "gls"}:
            if not hasattr(self.api, "get_parcel"):
                return None
            if self.courier == "gls":
                uid = self._get_gls_tracking_uid(tracking_number)
                if not uid:
                    _LOGGER.debug("GLS: cannot find trackingUid for shipmentNo=%s", tracking_number)
                    return None
                data = await self.api.get_parcel(uid)
                self._persist_auth_if_changed()
            else:
                data = await self.api.get_parcel(tracking_number)
            return self._extract_single_parcel(data, tracking_number)

        if self.courier == "pocztex":
            if not hasattr(self.api, "get_parcel_details"):
                return None
            detail_id = tracking_number
            current_data = self.data or []
            existing_parcel = next(
                (
                    item
                    for item in current_data
                    if str(get_parcel_id(item, self.courier) or "") == str(tracking_number)
                ),
                None,
            )
            if isinstance(existing_parcel, dict):
                detail_id = get_parcel_detail_id(existing_parcel, self.courier) or tracking_number

            data = await self.api.get_parcel_details(detail_id)
            if not isinstance(data, dict):
                return None
            merged = dict(existing_parcel) if isinstance(existing_parcel, dict) else {}
            merged.update(data)
            merged["_raw_response"] = data
            return merged

        return None

    def _extract_single_parcel(self, data, tracking_number: str):
        """Extract a single parcel dict from varied courier response formats."""
        if isinstance(data, dict):
            candidate_dicts = [data]
            for key in ("parcel", "shipment", "package", "data", "item"):
                nested = data.get(key)
                if isinstance(nested, dict):
                    candidate_dicts.append(nested)
                elif isinstance(nested, list):
                    candidate_dicts.extend([x for x in nested if isinstance(x, dict)])
            for candidate in candidate_dicts:
                if str(get_parcel_id(candidate, self.courier) or "") == str(tracking_number):
                    return candidate
            return data

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and str(get_parcel_id(item, self.courier) or "") == str(tracking_number):
                    return item
            return None

        return None

    def _filter_active_parcels(self, parcels):
        """Keep only active parcels this account should show."""
        if not isinstance(parcels, list):
            return []

        active = []
        for parcel in parcels:
            if not isinstance(parcel, dict):
                continue

            parcel_id = get_parcel_id(parcel, self.courier)
            raw_status = get_raw_status(parcel, self.courier)

            # 1. Delivery criterion: exclude delivered or terminal parcels
            if is_delivered(parcel, self.courier):
                _LOGGER.debug(
                    "Filtered out delivered/terminal parcel %s (%s)",
                    parcel_id,
                    raw_status,
                )
                continue

            # 2. Dead label criterion: exclude stale labels without movement
            if is_dead_label(parcel, self.courier):
                _LOGGER.debug(
                    "Filtered out stale dead label parcel %s (%s)",
                    parcel_id,
                    raw_status,
                )
                continue

            # 3. Hidden by the user in the account options
            if is_hidden_shipment(parcel, self.courier, self._hidden_shipments):
                self.hidden_tracking_numbers |= get_parcel_tracking_numbers(
                    parcel, self.courier
                )
                _LOGGER.debug("Filtered out hidden parcel %s", parcel_id)
                continue

            # 4. Recipient filter
            if not matches_recipient_filters(
                parcel, self._include_recipients, self._exclude_recipients
            ):
                _LOGGER.debug(
                    "Filtered out parcel %s due to recipient filter",
                    parcel_id,
                )
                continue

            active.append(parcel)

        if self.courier == "allegro":
            # An order shipped with a carrier the user also has an account
            # for is shown by that account; Allegro only adds order details.
            tracked = self._carrier_tracking_numbers()
            active = [
                parcel
                for parcel in active
                if not (get_parcel_tracking_numbers(parcel, self.courier) & tracked)
            ]
        _LOGGER.debug(
            "_filter_active_parcels [%s]: %d total fetched, %d active",
            self.courier,
            len(parcels),
            len(active),
        )
        return active

    @callback
    def async_hide_shipment(self, tracking_number: str) -> None:
        """Add a parcel to the account's hidden shipments option.

        Updating the options reloads the entry, which drops the parcel's
        sensor and buttons. Removing the number in Configure shows it again.
        """
        current = self.entry.options.get(CONF_HIDDEN_SHIPMENTS, "")
        updated = add_hidden_shipment(current, tracking_number)
        if updated == current:
            return
        _LOGGER.debug("Hiding shipment %s (%s)", tracking_number, self.courier)
        self.hass.config_entries.async_update_entry(
            self.entry,
            options={**self.entry.options, CONF_HIDDEN_SHIPMENTS: updated},
        )

    async def async_refresh_parcel(self, tracking_number: str) -> None:
        """Refresh a single parcel when courier API supports it.

        Falls back to full coordinator refresh if single fetch fails or returns unknown shape.
        """
        try:
            parcel = await self._fetch_single_parcel_with_retry(tracking_number)
            self._persist_auth_if_changed()
        except Exception as err:
            _LOGGER.debug(
                "Single parcel refresh failed for %s %s, falling back to full refresh: %s",
                self.courier,
                tracking_number,
                err,
            )
            await self.async_request_refresh()
            return

        if not isinstance(parcel, dict):
            await self.async_request_refresh()
            return

        current_data = list(self.data or [])
        replaced = False
        for idx, item in enumerate(current_data):
            if str(get_parcel_id(item, self.courier) or "") == str(tracking_number):
                current_data[idx] = parcel
                replaced = True
                break

        if not replaced:
            current_data.append(parcel)

        events, _, _ = reconcile_departed_parcels(
            self.data, current_data, self.courier, self._missing_parcel_counts
        )
        self.pending_lifecycle_events = events
        self._missing_parcel_counts.pop(str(tracking_number), None)
        filtered = self._filter_active_parcels(current_data)
        self.async_set_updated_data(filtered)

    async def _refresh_token(self):
        """Refresh API token and update config entry."""
        if self.courier == "inpost":
            await self.api.refresh_token()
            new_data = {
                **self.entry.data,
                CONF_TOKEN: self.api._token,
                CONF_REFRESH_TOKEN: self.api._refresh_token,
                CONF_TOKEN_EXPIRES_AT: self.api._expires_at,
            }
        elif self.courier == "dpd":
            await self.api.refresh_access_token()
            new_data = {
                **self.entry.data,
                CONF_TOKEN: self.api._token,
                CONF_REFRESH_TOKEN: self.api._refresh_token,
                CONF_TOKEN_EXPIRES_AT: self.api._expires_at,
            }
        elif self.courier == "dhl":
            await self.api.refresh_token()
            new_data = {
                **self.entry.data,
                CONF_TOKEN: self.api._token,
                "cookies": json.dumps(self.api._cookies),
            }
        elif self.courier == "pocztex":
            await self.api.refresh_token()
            new_data = {
                **self.entry.data,
                CONF_TOKEN: self.api._token,
                CONF_REFRESH_TOKEN: self.api._refresh_token,
                CONF_TOKEN_EXPIRES_AT: self.api._expires_at,
                CONF_REFRESH_EXPIRES_AT: self.api._refresh_expires_at,
            }
        elif self.courier == "gls":
            await self.api.refresh_token()
            await self.api.ensure_session()
            new_data = {
                **self.entry.data,
                CONF_TOKEN: self.api._token,
                CONF_REFRESH_TOKEN: self.api._refresh_token,
                CONF_ID_TOKEN: self.api._id_token,
                CONF_TOKEN_EXPIRES_AT: self.api._expires_at,
                CONF_SESSION_ID: self.api._session_id,
                CONF_SESSION_REGISTERED: self.api._session_registered,
            }
        else:
            return

        self.hass.config_entries.async_update_entry(self.entry, data=new_data)

    def _persist_auth_if_changed(self):
        """Persist token changes made by proactive in-request refreshes.

        The APIs refresh tokens on their own inside request(); without this the
        config entry keeps the tokens from setup time and a restart would come
        up with long-stale credentials.
        """
        if self.courier == "pocztex":
            new_data = {
                **self.entry.data,
                CONF_TOKEN: self.api._token,
                CONF_REFRESH_TOKEN: self.api._refresh_token,
                CONF_TOKEN_EXPIRES_AT: self.api._expires_at,
                CONF_REFRESH_EXPIRES_AT: self.api._refresh_expires_at,
            }
        elif self.courier in ("dpd", "inpost"):
            new_data = {
                **self.entry.data,
                CONF_TOKEN: self.api._token,
                CONF_REFRESH_TOKEN: self.api._refresh_token,
                CONF_TOKEN_EXPIRES_AT: self.api._expires_at,
            }
        elif self.courier == "gls":
            new_data = {
                **self.entry.data,
                CONF_TOKEN: self.api._token,
                CONF_REFRESH_TOKEN: self.api._refresh_token,
                CONF_ID_TOKEN: self.api._id_token,
                CONF_TOKEN_EXPIRES_AT: self.api._expires_at,
                CONF_SESSION_ID: self.api._session_id,
                CONF_SESSION_REGISTERED: self.api._session_registered,
            }
        else:
            return

        if new_data != self.entry.data:
            self.hass.config_entries.async_update_entry(self.entry, data=new_data)
