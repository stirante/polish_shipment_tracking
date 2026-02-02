import json
from pathlib import Path
from typing import Final

DOMAIN = "polish_shipment_tracking"
LEGACY_DOMAIN = "shipment_tracking"
PLATFORMS = ["sensor", "binary_sensor"]

CONF_COURIER = "courier"
CONF_PHONE = "phone"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_TOKEN = "token"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_TOKEN_EXPIRES_AT = "token_expires_at"
CONF_REFRESH_EXPIRES_AT = "refresh_expires_at"
CONF_DEVICE_UID = "device_uid"

# --- Frontend registration constants ---
_MANIFEST_PATH: Final[Path] = Path(__file__).parent / "manifest.json"


def _load_integration_version(manifest_path: Path) -> str:
    """Read the integration version from manifest.json with safe fallbacks."""
    try:
        manifest_text = manifest_path.read_text(encoding="utf-8")
        manifest_data = json.loads(manifest_text)
    except (OSError, json.JSONDecodeError):
        return "0.0.0"
    return str(manifest_data.get("version", "0.0.0"))


INTEGRATION_VERSION: Final[str] = _load_integration_version(_MANIFEST_PATH)

URL_BASE: Final[str] = "/polish-shipment-tracking"

# List of JavaScript modules to register with Lovelace.
JSMODULES: Final[list[dict[str, str]]] = [
    {
        "name": "Shipment Tracking Card",
        "filename": "shipment-tracking-card.js",
        "version": INTEGRATION_VERSION,
    }
]
