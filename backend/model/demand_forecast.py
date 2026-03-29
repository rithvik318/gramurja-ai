"""
Demand Forecast Model - Predicts next-day electricity demand.
Uses smart_meter.csv with Linear Regression (simple ML for prototype).
"""

import pandas as pd
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_SMART_METER_PATH = _DATA_DIR / "smart_meter.csv"

# Load and fit model at module load
_df = pd.read_csv(_SMART_METER_PATH)
_X = _df[["hour", "temperature"]]
_y = _df["consumption"]

from sklearn.linear_model import LinearRegression

_model = LinearRegression()
_model.fit(_X, _y)


def predict_demand(hour: int, temperature: float) -> float:
    """Predict demand in kW for a given hour and temperature."""
    import pandas as pd
    X = pd.DataFrame([[hour, temperature]], columns=["hour", "temperature"])
    prediction = _model.predict(X)
    return float(prediction[0])


def get_next_day_demand_forecast() -> dict:
    """
    Returns next-day demand forecast.
    Uses average of historical hourly pattern with temperature adjustment.
    """
    import numpy as np

    # Next day: assume similar temp profile, use moving average of historical
    hourly_demands = []
    for _, row in _df.iterrows():
        h, t = int(row["hour"]), float(row["temperature"])
        d = predict_demand(h, t)
        hourly_demands.append(d)

    # Predicted daily total (kWh) - sum of hourly kW
    total_demand_kwh = sum(hourly_demands)
    # Average hourly demand for "typical" next day
    avg_demand_kw = np.mean(hourly_demands)

    return {
        "predicted_daily_demand_kwh": round(float(total_demand_kwh), 2),
        "predicted_avg_demand_kw": round(float(avg_demand_kw), 2),
        "hourly_forecast": [round(float(d), 2) for d in hourly_demands],
    }
