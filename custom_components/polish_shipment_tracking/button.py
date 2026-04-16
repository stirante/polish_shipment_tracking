from __future__ import annotations

import logging
from collections.abc import Callable

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_EMAIL, CONF_PHONE, DOMAIN, INTEGRATION_VERSION
from .coordinator import ShipmentCoordinator
from .helpers import get_parcel_id, is_delivered

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[list[ButtonEntity]], None],
) -> None:
    """Set up button entities from a config entry."""
    coordinator: ShipmentCoordinator = hass.data[DOMAIN][entry.entry_id]

    @callback
    def async_update_buttons() -> None:
        """Add new parcel refresh buttons and remove old ones."""
        registry = async_get_entity_registry(hass)
        current_data = coordinator.data or []

        refresh_all_unique_id = _get_refresh_all_unique_id(coordinator)
        refresh_all_entity_id = registry.async_get_entity_id("button", DOMAIN, refresh_all_unique_id)
        if _should_add_runtime_entity(hass, registry, entry, refresh_all_entity_id):
            async_add_entities([RefreshAllShipmentsButton(coordinator)])

        current_ids = set()
        new_buttons = []
        for parcel in current_data:
            pid = get_parcel_id(parcel, coordinator.courier)
            if not pid or is_delivered(parcel, coordinator.courier):
                continue

            current_ids.add(pid)
            unique_id = _get_refresh_unique_id(coordinator.courier, pid)
            existing_entity_id = registry.async_get_entity_id("button", DOMAIN, unique_id)
            if not _should_add_runtime_entity(hass, registry, entry, existing_entity_id):
                continue

            new_buttons.append(RefreshShipmentButton(coordinator, pid))

        if new_buttons:
            async_add_entities(new_buttons)

        if coordinator.courier == "dpd":
            manage_buttons = []
            for pid in current_ids:
                unique_id = _get_manage_unique_id(coordinator.courier, pid)
                existing_entity_id = registry.async_get_entity_id("button", DOMAIN, unique_id)
                if not _should_add_runtime_entity(hass, registry, entry, existing_entity_id):
                    continue
                manage_buttons.append(ManageShipmentButton(coordinator, pid))

            if manage_buttons:
                async_add_entities(manage_buttons)

        _async_remove_old_parcel_buttons(
            hass,
            entry,
            coordinator,
            current_ids,
        )

    entry.async_on_unload(coordinator.async_add_listener(async_update_buttons))
    async_update_buttons()


def _async_remove_old_parcel_buttons(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator: ShipmentCoordinator,
    current_ids: set[str],
) -> None:
    """Remove per-parcel buttons that no longer match active shipments."""
    registry = async_get_entity_registry(hass)
    current_unique_ids = {_get_refresh_unique_id(coordinator.courier, pid) for pid in current_ids}
    if coordinator.courier == "dpd":
        current_unique_ids |= {_get_manage_unique_id(coordinator.courier, pid) for pid in current_ids}

    entities_to_remove = []
    for entity_entry in registry.entities.values():
        unique_id = entity_entry.unique_id or ""
        if (
            entity_entry.platform == DOMAIN
            and entity_entry.config_entry_id == entry.entry_id
            and entity_entry.entity_id.startswith("button.")
            and (unique_id.endswith("_refresh") or unique_id.endswith("_manage"))
            and unique_id not in current_unique_ids
        ):
            entities_to_remove.append(entity_entry.entity_id)

    for entity_id in entities_to_remove:
        registry.async_remove(entity_id)


def _should_add_runtime_entity(
    hass: HomeAssistant,
    registry,
    entry: ConfigEntry,
    entity_id: str | None,
) -> bool:
    """Return True if runtime entity should be created for this entry."""
    if entity_id is None:
        return True

    existing = registry.async_get(entity_id)
    if existing and existing.config_entry_id != entry.entry_id:
        # Another account already owns this unique ID.
        return False

    # Registry entry exists for this account but runtime state is missing.
    return entity_id not in hass.states


def _get_refresh_all_unique_id(coordinator: ShipmentCoordinator) -> str:
    return f"{coordinator.courier}_{coordinator.entry.entry_id}_refresh_all"


def _get_refresh_unique_id(courier: str, tracking_number: str) -> str:
    return f"{courier}_{tracking_number}_refresh"


def _get_manage_unique_id(courier: str, tracking_number: str) -> str:
    return f"{courier}_{tracking_number}_manage"


def _build_device_info(coordinator: ShipmentCoordinator) -> DeviceInfo:
    account_id = coordinator.entry.data.get(CONF_PHONE) or coordinator.entry.data.get(CONF_EMAIL)
    return DeviceInfo(
        identifiers={(DOMAIN, coordinator.entry.entry_id)},
        name=f"{coordinator.courier.title()} ({account_id})",
        manufacturer="Polish Shipment Tracking",
        model=coordinator.courier.title(),
        sw_version=INTEGRATION_VERSION,
    )


class RefreshAllShipmentsButton(CoordinatorEntity[ShipmentCoordinator], ButtonEntity):
    """Button to refresh all shipments for the account."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: ShipmentCoordinator) -> None:
        """Initialize the refresh-all button."""
        super().__init__(coordinator)
        self._attr_name = "Refresh shipments"
        self._attr_unique_id = _get_refresh_all_unique_id(coordinator)
        self._attr_device_info = _build_device_info(coordinator)

    async def async_press(self) -> None:
        """Request manual refresh for the whole coordinator."""
        _LOGGER.debug("Manual refresh requested for all shipments (%s)", self.coordinator.courier)
        await self.coordinator.async_request_refresh()

    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes for card discovery."""
        return {
            "integration_domain": DOMAIN,
            "courier": self.coordinator.courier,
            "refresh_scope": "all",
        }


class RefreshShipmentButton(CoordinatorEntity[ShipmentCoordinator], ButtonEntity):
    """Button to refresh shipment data."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:package-up"

    def __init__(self, coordinator: ShipmentCoordinator, tracking_number: str) -> None:
        """Initialize the per-shipment refresh button."""
        super().__init__(coordinator)
        self._tracking_number = tracking_number
        self._attr_name = f"Refresh shipment {tracking_number}"
        self._attr_unique_id = _get_refresh_unique_id(coordinator.courier, tracking_number)
        self._attr_device_info = _build_device_info(coordinator)

    async def async_press(self) -> None:
        """Request manual refresh for this shipment."""
        _LOGGER.debug(
            "Manual refresh requested for shipment %s (%s)",
            self._tracking_number,
            self.coordinator.courier,
        )
        await self.coordinator.async_refresh_parcel(self._tracking_number)

    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes for card discovery."""
        return {
            "integration_domain": DOMAIN,
            "courier": self.coordinator.courier,
            "tracking_number": self._tracking_number,
            "refresh_scope": "single",
        }


class ManageShipmentButton(CoordinatorEntity[ShipmentCoordinator], ButtonEntity):
    """Button to fetch DPD manage URL for a shipment."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:link-variant"

    def __init__(self, coordinator: ShipmentCoordinator, tracking_number: str) -> None:
        """Initialize the per-shipment manage button."""
        super().__init__(coordinator)
        self._tracking_number = tracking_number
        self._attr_name = f"Manage shipment {tracking_number}"
        self._attr_unique_id = _get_manage_unique_id(coordinator.courier, tracking_number)
        self._attr_device_info = _build_device_info(coordinator)

    async def async_press(self) -> None:
        """Fetch and publish a DPD management URL for this shipment."""
        if not hasattr(self.coordinator.api, "get_manage_package_url"):
            _LOGGER.debug(
                "DPD management URL API not available for %s",
                self._tracking_number,
            )
            return

        try:
            manage_resp = await self.coordinator.api.get_manage_package_url(self._tracking_number)
        except Exception as err:
            _LOGGER.warning(
                "DPD manage URL response for %s: %s",
                self._tracking_number,
                err,
            )
            return

        _LOGGER.debug(
            "DPD manage URL response for %s: %s",
            self._tracking_number,
            manage_resp,
        )
        manage_url = None
        if isinstance(manage_resp, dict):
            manage_url = (
                manage_resp.get("link")
                or manage_resp.get("url")
                or manage_resp.get("managementUrl")
            )
        elif isinstance(manage_resp, str):
            manage_url = manage_resp

        if not manage_url:
            _LOGGER.warning(
                "DPD management URL missing in response for %s: %s",
                self._tracking_number,
                manage_resp,
            )
            return

        self.coordinator.hass.bus.async_fire(
            f"{DOMAIN}_manage_url",
            {
                "courier": self.coordinator.courier,
                "tracking_number": self._tracking_number,
                "manage_url": manage_url,
            },
        )

    @property
    def extra_state_attributes(self) -> dict:
        """Return attributes for card discovery."""
        return {
            "integration_domain": DOMAIN,
            "courier": self.coordinator.courier,
            "tracking_number": self._tracking_number,
            "action": "manage_url",
        }
