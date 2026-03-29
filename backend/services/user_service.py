import copy
import json
from pathlib import Path
from typing import Any, Dict, Optional

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "user_profile.json"

DEFAULT_PROFILE: Dict[str, Any] = {
    "state": "",
    "language": "en",
    "house": {"type": "", "rooms": "", "people": ""},
    "appliances": [],
    "applianceDetails": [],
    "bill": "",
    "solar": {"hasSolar": False, "capacity": "", "netMetering": False},
    "usagePattern": "",
    "goal": "",
}


def _deep_merge(base: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    for key, val in incoming.items():
        if (
            key in out
            and isinstance(out[key], dict)
            and isinstance(val, dict)
        ):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def _normalize_profile(p: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure expected shapes and keep appliances in sync with applianceDetails."""
    house = p.get("house") if isinstance(p.get("house"), dict) else {}
    p["house"] = {
        "type": str(house.get("type", "")),
        "rooms": str(house.get("rooms", "")),
        "people": str(house.get("people", "")),
    }
    solar = p.get("solar") if isinstance(p.get("solar"), dict) else {}
    p["solar"] = {
        "hasSolar": bool(solar.get("hasSolar", False)),
        "capacity": str(solar.get("capacity", "")),
        "netMetering": bool(solar.get("netMetering", False)),
    }
    details = p.get("applianceDetails")
    if not isinstance(details, list):
        details = []
    clean_details = []
    for item in details:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        try:
            count = int(item.get("count", 1))
        except (TypeError, ValueError):
            count = 1
        try:
            hours = float(item.get("hours", 0))
        except (TypeError, ValueError):
            hours = 0.0
        clean_details.append(
            {"name": str(item["name"]), "count": max(1, count), "hours": max(0.0, hours)}
        )
    p["applianceDetails"] = clean_details
    apps = p.get("appliances")
    if not isinstance(apps, list):
        apps = []
    apps = [str(a) for a in apps if a]
    if clean_details:
        seen = []
        for d in clean_details:
            n = d["name"]
            if n not in seen:
                seen.append(n)
        p["appliances"] = seen
    else:
        p["appliances"] = apps
    p["state"] = str(p.get("state", ""))
    p["language"] = str(p.get("language", "en") or "en")
    p["bill"] = str(p.get("bill", ""))
    p["usagePattern"] = str(p.get("usagePattern", ""))
    p["goal"] = str(p.get("goal", ""))
    return p


def save_user_profile(data: dict) -> None:
    """Merge incoming onboarding payload with defaults and persist full profile."""
    current = get_user_profile()
    base = _deep_merge(DEFAULT_PROFILE, current) if current else copy.deepcopy(DEFAULT_PROFILE)
    merged = _deep_merge(base, data if isinstance(data, dict) else {})
    profile = _normalize_profile(merged)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)


def get_user_profile() -> Optional[dict]:
    """Return profile dict if file exists, else None."""
    if not DATA_PATH.exists():
        return None
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, dict):
            return None
        return _normalize_profile(_deep_merge(DEFAULT_PROFILE, raw))
    except (json.JSONDecodeError, OSError):
        return None
