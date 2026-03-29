"""
Analytics Service - Provides insights on consumption, costs, appliance usage.
Data sources: smart_meter.csv, appliances.csv
"""

import pandas as pd
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_SMART_METER_PATH = _DATA_DIR / "smart_meter.csv"
_APPLIANCES_PATH = _DATA_DIR / "appliances.csv"
_TARIFFS_PATH = _DATA_DIR / "tariffs.csv"


def get_analytics_summary() -> dict:
    """
    Returns analytics summary:
    - daily_consumption_kwh
    - monthly_cost_estimate
    - top_appliance
    - appliance_energy_distribution (optional)
    """
    df_meter = pd.read_csv(_SMART_METER_PATH)
    df_appliances = pd.read_csv(_APPLIANCES_PATH) if _APPLIANCES_PATH.exists() else pd.DataFrame()
    df_tariffs = pd.read_csv(_TARIFFS_PATH) if _TARIFFS_PATH.exists() else pd.DataFrame()

    # Daily consumption = sum of hourly consumption (smart_meter represents typical day)
    daily_consumption_kwh = float(df_meter["consumption"].sum())

    # Monthly estimate (30 days)
    monthly_kwh = daily_consumption_kwh * 30

    # Cost: use average tariff if available
    if not df_tariffs.empty and "price_per_kwh" in df_tariffs.columns:
        avg_price = float(df_tariffs["price_per_kwh"].mean())
        monthly_cost_estimate = round(monthly_kwh * avg_price, 2)
    else:
        monthly_cost_estimate = round(monthly_kwh * 0.18, 2)  # default 18¢/kWh

    # Top appliance: highest power * typical usage
    if not df_appliances.empty and "power_kw" in df_appliances.columns:
        df_appliances = df_appliances.copy()
        df_appliances["energy_share"] = (
            df_appliances["power_kw"] * df_appliances.get("duration_hours", 1)
        )
        top_row = df_appliances.loc[df_appliances["energy_share"].idxmax()]
        top_appliance = str(top_row["appliance"])
        # Appliance distribution (simplified: proportional to power*duration)
        total_share = df_appliances["energy_share"].sum()
        appliance_distribution = {
            str(row["appliance"]): round(float(100 * row["energy_share"] / total_share), 1)
            for _, row in df_appliances.iterrows()
        }
    else:
        top_appliance = "Air Conditioner"  # fallback
        appliance_distribution = {}

    return {
        "daily_consumption_kwh": round(daily_consumption_kwh, 2),
        "monthly_cost_estimate": monthly_cost_estimate,
        "top_appliance": top_appliance,
        "appliance_distribution": appliance_distribution,
    }
