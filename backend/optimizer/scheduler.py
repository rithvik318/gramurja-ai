"""
Smart Scheduler - Recommends optimal times to run appliances.
Based on: solar production forecast, electricity tariffs, appliance energy usage.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_APPLIANCES_PATH = _DATA_DIR / "appliances.csv"
_TARIFFS_PATH = _DATA_DIR / "tariffs.csv"


def _load_appliances() -> List[Dict[str, Any]]:
    """Load appliances with power and duration."""
    df = pd.read_csv(_APPLIANCES_PATH)
    return df.to_dict(orient="records")


def _load_tariffs() -> List[Dict[str, Any]]:
    """Load hourly tariff prices."""
    df = pd.read_csv(_TARIFFS_PATH)
    return df.to_dict(orient="records")


def _get_solar_forecast_by_hour() -> List[float]:
    """Get hourly solar forecast (import to avoid circular deps at module level)."""
    from backend.model.solar_forecast import get_next_day_solar_forecast
    data = get_next_day_solar_forecast()
    return data.get("hourly_forecast", [0] * 24)


def optimize_schedule(
    appliances: List[Dict[str, Any]] = None,
    solar_by_hour: List[float] = None,
    tariffs: List[Dict[str, Any]] = None,
) -> List[Dict[str, str]]:
    """
    Recommends best hour to run each appliance.
    Optimizes for: high solar production + low tariff price.
    """
    appliances = appliances or _load_appliances()
    tariffs = tariffs or _load_tariffs()
    solar_by_hour = solar_by_hour or _get_solar_forecast_by_hour()

    # Ensure we have 24 hours of solar (pad if needed)
    while len(solar_by_hour) < 24:
        solar_by_hour.append(0)

    # Build tariff by hour (0-23)
    tariff_by_hour = {int(t["hour"]): float(t["price_per_kwh"]) for t in tariffs}
 
    schedule = []

    for app in appliances:
        name = app.get("appliance", app.get("name", "Unknown"))
        power_kw = float(app.get("power_kw", app.get("power", 1.0)))
        duration = float(app.get("duration_hours", 1.0))

        best_hour = 12
        best_score = float("-inf")

        # Score = solar_available - cost_factor
        # Higher solar = better, lower price = better
        for hour in range(24):
            solar = solar_by_hour[hour] if hour < len(solar_by_hour) else 0
            price = tariff_by_hour.get(hour, 0.18)

            # Solar bonus: more solar = better
            solar_score = solar * 2  # weight solar heavily
            # Cost penalty: higher price = worse
            cost_penalty = price * 10

            score = solar_score - cost_penalty

            if score > best_score:
                best_score = score
                best_hour = hour

        schedule.append({
            "appliance": name,
            "recommended_hour": best_hour,
        })

    return schedule
