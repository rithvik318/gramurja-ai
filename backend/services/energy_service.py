"""
Energy Service - Simulates live home energy state.
Uses smart_meter.csv as base data with random variation (simulates IoT/Azure IoT Hub streaming).
"""

import random
import pandas as pd
from pathlib import Path

# Resolve data path relative to this file
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_SMART_METER_PATH = _DATA_DIR / "smart_meter.csv"


def _load_smart_meter_base() -> pd.DataFrame:
    """Load smart meter data - simulates data stream from Azure IoT Hub."""
    return pd.read_csv(_SMART_METER_PATH)


def get_live_energy() -> dict:
    """
    Returns live home energy state.
    Simulates IoT data by using smart_meter hourly pattern + random variation.
    """
    df = _load_smart_meter_base()
    # Use current hour (or random if demo) - weighted toward daytime for demo
    hour = random.randint(8, 17)  # 8 AM - 5 PM typical solar hours
    base_row = df[df["hour"] == hour].iloc[0]

    base_consumption = float(base_row["consumption"])
    base_temp = float(base_row["temperature"])

    # Random variation: ±15% simulates real-time fluctuations
    variation = random.uniform(0.85, 1.15)
    home_consumption_kw = round(base_consumption * variation, 2)

    # Solar: peak at noon, 0 at night (6-18 range)
    if 6 <= hour <= 18:
        peak_solar = 5.5
        # Solar curve: peaks at 12
        solar_factor = 1 - abs(12 - hour) / 6
        base_solar = peak_solar * max(0.3, solar_factor)
    else:
        base_solar = 0.0

    solar_variation = random.uniform(0.9, 1.1)
    solar_generation_kw = round(max(0, base_solar * solar_variation), 2)

    # Grid export = solar - consumption (when solar > consumption)
    grid_export_kw = round(max(0, solar_generation_kw - home_consumption_kw), 2)

    # Battery: higher when solar is producing, slight random variation
    if solar_generation_kw > 2:
        battery_base = random.randint(80, 95)
    else:
        battery_base = random.randint(60, 85)
    battery_percent = battery_base + random.randint(-2, 2)
    battery_percent = max(0, min(100, battery_percent))

    return {
        "solar_generation_kw": solar_generation_kw,
        "home_consumption_kw": home_consumption_kw,
        "grid_export_kw": grid_export_kw,
        "battery_percent": battery_percent,
    }
