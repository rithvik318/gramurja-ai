"""
Solar Forecast Model - Estimates solar output based on time and simulated weather.
Simulates Azure Maps Weather API integration for irradiance, cloud cover, temperature.
"""

import random
from datetime import datetime
from typing import Optional


def _simulate_azure_maps_weather(hour: int) -> dict:
    """
    Simulates Azure Maps Weather API response.
    In production, would call: Azure Maps Get Weather Data API
    Returns: cloud_cover (%), solar_irradiance (W/m²), temperature (°C)
    """
    # Day/night cycle
    if hour < 6 or hour > 18:
        return {
            "cloud_cover": random.randint(0, 30),
            "solar_irradiance": 0,
            "temperature": 22 + (hour - 12) * 0.5 if hour <= 12 else 22 - (hour - 12) * 0.3,
        }

    # Daytime: irradiance peaks at solar noon (~12-13)
    solar_noon = 12.5
    # Simple clear-sky curve
    hour_angle = abs(hour - solar_noon)
    max_irradiance = 1000  # W/m² clear sky max
    irradiance_factor = max(0, 1 - (hour_angle / 6) ** 1.5)

    base_irradiance = max_irradiance * irradiance_factor

    # Simulated weather variability
    cloud_cover = random.randint(10, 40)  # % cloud cover
    cloud_reduction = 1 - (cloud_cover / 100) * 0.7  # clouds reduce irradiance
    solar_irradiance = int(base_irradiance * cloud_reduction * random.uniform(0.9, 1.1))

    # Temperature curve: warmer midday
    temp_base = 25 + (4 - abs(hour - 14)) * 1.5
    temperature = round(temp_base + random.uniform(-2, 2), 1)

    return {
        "cloud_cover": cloud_cover,
        "solar_irradiance": solar_irradiance,
        "temperature": temperature,
    }


def predict_solar(
    hour: Optional[int] = None,
    cloud_cover: Optional[int] = None,
    solar_irradiance: Optional[float] = None,
) -> float:
    """
    Estimate solar generation in kW.
    Uses simulated Azure Maps weather (or passed params) + time of day.
    """
    if hour is None:
        hour = datetime.now().hour

    weather = _simulate_azure_maps_weather(hour)

    if cloud_cover is not None:
        weather["cloud_cover"] = cloud_cover
    if solar_irradiance is not None:
        weather["solar_irradiance"] = solar_irradiance

    irrad = weather["solar_irradiance"]
    cloud = weather["cloud_cover"]

    # Convert irradiance (W/m²) to kW output for typical 5kW system
    # 5kW system ≈ 25m², efficiency ~20%, so: irrad * 25 * 0.2 / 1000 = kW
    system_capacity_kw = 5.0
    panel_area_m2 = 25
    efficiency = 0.2
    base_kw = (irrad / 1000) * panel_area_m2 * efficiency

    # Cloud adjustment
    cloud_factor = 1 - (cloud / 100) * 0.6
    predicted_kw = base_kw * cloud_factor

    noise = random.uniform(-0.2, 0.2)
    return max(0, round(predicted_kw + noise, 2))


def get_next_day_solar_forecast() -> dict:
    """Returns next-day solar generation forecast (average and peak)."""
    hourly_solar = []
    for h in range(24):
        s = predict_solar(h)
        hourly_solar.append(round(s, 2))

    total_solar_kwh = sum(hourly_solar)
    peak_solar_kw = max(hourly_solar) if hourly_solar else 0
    peak_hour = hourly_solar.index(peak_solar_kw) if hourly_solar else 12

    return {
        "predicted_solar_kwh": round(total_solar_kwh, 2),
        "predicted_peak_solar_kw": round(peak_solar_kw, 2),
        "peak_hour": peak_hour,
        "hourly_forecast": hourly_solar,
    }


def get_simulated_weather(hour: int) -> dict:
    """Expose simulated Azure Maps weather for demo/testing."""
    return _simulate_azure_maps_weather(hour)
