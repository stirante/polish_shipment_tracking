"""When parcels go out for delivery and arrive, and what that predicts.

RECORDS keeps one entry per parcel: where it goes and the times it was handed
out for delivery and arrived. "Where" is the pickup point, or for a courier
delivery to the door "home:<courier>[:<address>]", because each courier has
its own route. Prediction looks only at parcels that went to the same place,
because the courier's route decides the hour.
"""
from __future__ import annotations

import re
import statistics
from datetime import datetime, timedelta

HANDED_OUT = "handed_out_for_delivery"
ARRIVED = "waiting_for_pickup"
MIN_SAMPLES = 3

HOME_PREFIX = "home:"

# tracking number -> {"point", "courier", "shipment_id", "handed_out", "arrived"} (ISO strings)
RECORDS: dict[str, dict] = {}

_MONTHS = {
    "sty": 1, "lut": 2, "mar": 3, "kwi": 4, "maj": 5, "cze": 6,
    "lip": 7, "sie": 8, "wrz": 9, "paź": 10, "lis": 11, "gru": 12,
}
_HINT_RE = re.compile(
    r"(\d{1,2})\s+(sty|lut|mar|kwi|maj|cze|lip|sie|wrz|paź|lis|gru)\w*\.?\s*(?:(\d{4}),?)?\s+(\d{1,2}):(\d{2})"
)
_ALLEGRO_STEPS = {"IN_DELIVERY": HANDED_OUT, "AVAILABLE_FOR_PICKUP": ARRIVED}


def point_key(location) -> str | None:
    if not location:
        return None
    return " ".join(str(location).lower().split()) or None


def delivery_place(courier, pickup_point, delivery_address=None) -> str:
    """The pickup point, or the courier's route to the door when there is none."""
    if pickup_point:
        return str(pickup_point)
    place = f"{HOME_PREFIX}{courier}"
    return f"{place}:{delivery_address}" if delivery_address else place


def is_home(place) -> bool:
    return bool(place) and str(place).lower().startswith(HOME_PREFIX)


def parse_hint(hint, now: datetime) -> datetime | None:
    """Read an Allegro timeline hint like 'Od wt. 17 lis 09:05' in now's timezone."""
    if not hint:
        return None
    match = _HINT_RE.search(str(hint))
    if not match:
        return None
    day, month, year, hour, minute = match.groups()
    try:
        when = now.replace(
            year=int(year) if year else now.year,
            month=_MONTHS[month],
            day=int(day),
            hour=int(hour),
            minute=int(minute),
            second=0,
            microsecond=0,
        )
    except ValueError:
        return None
    # Hints without a year are recent: a date far ahead belongs to last year.
    if not year and when > now + timedelta(days=2):
        when = when.replace(year=when.year - 1)
    return when


def record(
    tracking_number, courier, location, status_key, when: datetime, overwrite: bool = True, shipment_id=None
) -> bool:
    """Store when a parcel went out or reached its point. Returns True if anything changed."""
    key = point_key(location)
    if not tracking_number or not key or status_key not in (HANDED_OUT, ARRIVED):
        return False
    if status_key == ARRIVED and is_home(key):
        # Waiting for pickup without a known point; a door delivery arrives
        # only when it is delivered (record_home_delivery).
        return False
    field = "handed_out" if status_key == HANDED_OUT else "arrived"
    entry = RECORDS.setdefault(str(tracking_number), {"point": key, "courier": courier})
    if shipment_id and entry.get("shipment_id") != str(shipment_id):
        entry["shipment_id"] = str(shipment_id)
    value = when.isoformat()
    if entry.get(field) == value or (entry.get(field) and not overwrite):
        return False
    entry["point"] = key
    entry[field] = value
    return True


def record_home_delivery(shipment_id, when: datetime) -> bool:
    """A parcel that went out to the door was delivered: that is its arrival."""
    changed = False
    for key, entry in RECORDS.items():
        if str(shipment_id) not in (key, entry.get("shipment_id")):
            continue
        if is_home(entry.get("point")) and entry.get("handed_out") and not entry.get("arrived"):
            entry["arrived"] = when.isoformat()
            changed = True
    return changed


def record_allegro_timeline(tracking_number, location, timeline, now: datetime) -> bool:
    """Take exact times from the Allegro timeline steps (IN_DELIVERY, AVAILABLE_FOR_PICKUP)."""
    changed = False
    for step in timeline or []:
        if not isinstance(step, dict):
            continue
        status_key = _ALLEGRO_STEPS.get(step.get("type"))
        when = parse_hint(step.get("hint"), now) if status_key else None
        if when:
            changed |= record(tracking_number, "allegro", location, status_key, when)
    return changed


def _minutes(dt: datetime) -> int:
    return dt.hour * 60 + dt.minute


def predict(location, handed_out: datetime) -> dict | None:
    """Expected arrival at the point for a parcel handed out at `handed_out`.

    Uses the hours other parcels reached this point that are later than the
    hand-out; with too few of those, the usual hand-out-to-arrival delay.
    """
    key = point_key(location)
    if not key:
        return None
    arrivals = []
    delays = []
    for entry in RECORDS.values():
        if entry.get("point") != key or not entry.get("arrived"):
            continue
        arrived = datetime.fromisoformat(entry["arrived"])
        arrivals.append(_minutes(arrived))
        if entry.get("handed_out"):
            out = datetime.fromisoformat(entry["handed_out"])
            delay = (arrived - out).total_seconds() / 60
            if 0 < delay < 16 * 60:
                delays.append(delay)

    start = _minutes(handed_out)
    later = sorted(m for m in arrivals if m >= start + 10)
    if len(later) >= MIN_SAMPLES:
        expected, earliest, latest, samples = statistics.median(later), later[0], later[-1], len(later)
    elif len(delays) >= MIN_SAMPLES:
        delays.sort()
        expected = start + statistics.median(delays)
        earliest, latest, samples = start + delays[0], start + delays[-1], len(delays)
    else:
        return None

    midnight = handed_out.replace(hour=0, minute=0, second=0, microsecond=0)
    return {
        "expected": midnight + timedelta(minutes=round(expected)),
        "earliest": midnight + timedelta(minutes=round(earliest)),
        "latest": midnight + timedelta(minutes=round(latest)),
        "samples": samples,
    }


def handed_out_at(tracking_number) -> datetime | None:
    entry = RECORDS.get(str(tracking_number)) or {}
    return datetime.fromisoformat(entry["handed_out"]) if entry.get("handed_out") else None
