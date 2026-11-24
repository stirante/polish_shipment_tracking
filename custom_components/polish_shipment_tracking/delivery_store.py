"""Keeps delivery_times.RECORDS in HA storage across restarts."""
from __future__ import annotations

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store

from . import delivery_times
from .const import DOMAIN

_STORE: Store | None = None
_SAVE_DELAY = 30
_MAX_RECORDS = 2000


async def async_load(hass: HomeAssistant) -> None:
    global _STORE
    if _STORE is not None:
        return
    _STORE = Store(hass, 1, f"{DOMAIN}.delivery_times")
    data = await _STORE.async_load() or {}
    delivery_times.RECORDS.clear()
    delivery_times.RECORDS.update(data.get("records") or {})


@callback
def async_save() -> None:
    if _STORE is None:
        return
    records = delivery_times.RECORDS
    if len(records) > _MAX_RECORDS:
        newest = sorted(records, key=lambda k: records[k].get("arrived") or records[k].get("handed_out") or "")
        for key in newest[: len(records) - _MAX_RECORDS]:
            records.pop(key)
    _STORE.async_delay_save(lambda: {"records": records}, _SAVE_DELAY)
