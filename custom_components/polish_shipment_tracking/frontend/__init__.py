"""JavaScript module registration for the Shipment Tracking integration.

This module exposes a helper class that registers static paths and
JavaScript modules with Lovelace so that custom cards bundled with the
integration are automatically available in the dashboard when using
storage mode.  The registration follows the pattern described in the
Home Assistant developer guide for embedded Lovelace cards.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later

from ..const import JSMODULES, URL_BASE

_LOGGER = logging.getLogger(__name__)


class JSModuleRegistration:
    """Registers JavaScript modules in Home Assistant for this integration."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the registrar with the given Home Assistant instance."""
        self.hass = hass
        # Access the Lovelace object; it may be None if Lovelace is not loaded yet.
        self.lovelace = self.hass.data.get("lovelace")

    async def async_register(self) -> None:
        """Register the static path and resources if needed."""
        await self._async_register_path()
        # Only attempt resource registration in storage mode.
        if self._is_storage_mode():
            await self._async_wait_for_lovelace_resources()

    def _is_storage_mode(self) -> bool:
        """Return True when Lovelace resources use storage mode.

        Home Assistant renamed ``lovelace.mode`` to ``lovelace.resource_mode``.
        Support both fields for compatibility across HA versions.
        """
        if not self.lovelace:
            return False

        mode = getattr(
            self.lovelace,
            "resource_mode",
            getattr(self.lovelace, "mode", None),
        )
        return mode == "storage"

    async def _async_register_path(self) -> None:
        """Register the static HTTP path for serving frontend files."""
        try:
            await self.hass.http.async_register_static_paths(
                [StaticPathConfig(URL_BASE, Path(__file__).parent, False)]
            )
            _LOGGER.debug("Path registered: %s -> %s", URL_BASE, Path(__file__).parent)
        except RuntimeError:
            # Path is already registered, which can happen on reload.
            _LOGGER.debug("Path already registered: %s", URL_BASE)

    async def _async_wait_for_lovelace_resources(self) -> None:
        """Wait until Lovelace resources are loaded then register modules."""

        async def _check_loaded(_now: Any) -> None:
            # If resources are loaded, register the modules; otherwise retry.
            if self.lovelace.resources.loaded:
                await self._async_register_modules()
            else:
                _LOGGER.debug("Lovelace resources not loaded, retrying in 5s")
                async_call_later(self.hass, 5, _check_loaded)

        await _check_loaded(0)

    async def _async_register_modules(self) -> None:
        """Register or update JavaScript modules in Lovelace resources."""
        _LOGGER.debug("Installing JavaScript modules for Shipment Tracking")
        # Find existing resources served by this integration.
        existing_resources = [
            r
            for r in self.lovelace.resources.async_items()
            if r["url"].startswith(URL_BASE)
        ]

        for module in JSMODULES:
            url = f"{URL_BASE}/{module['filename']}"
            registered = False
            for resource in existing_resources:
                if self._get_path(resource["url"]) == url:
                    registered = True
                    # Update version if mismatched
                    if self._get_version(resource["url"]) != module["version"]:
                        _LOGGER.info(
                            "Updating %s to version %s", module["name"], module["version"]
                        )
                        await self.lovelace.resources.async_update_item(
                            resource["id"],
                            {
                                "res_type": "module",
                                "url": f"{url}?v={module['version']}",
                            },
                        )
                    break
            if not registered:
                _LOGGER.info(
                    "Registering %s version %s", module["name"], module["version"]
                )
                await self.lovelace.resources.async_create_item(
                    {
                        "res_type": "module",
                        "url": f"{url}?v={module['version']}",
                    }
                )

    def _get_path(self, url: str) -> str:
        """Extract the path without query parameters."""
        return url.split("?")[0]

    def _get_version(self, url: str) -> str:
        """Extract the version parameter from the URL if present."""
        parts = url.split("?")
        if len(parts) > 1 and parts[1].startswith("v="):
            return parts[1].replace("v=", "")
        return "0"

    async def async_unregister(self) -> None:
        """Remove Lovelace resources registered by this integration."""
        if self._is_storage_mode():
            for module in JSMODULES:
                url = f"{URL_BASE}/{module['filename']}"
                resources = [
                    r
                    for r in self.lovelace.resources.async_items()
                    if r["url"].startswith(url)
                ]
                for resource in resources:
                    await self.lovelace.resources.async_delete_item(resource["id"])
