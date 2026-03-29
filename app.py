"""
GramUrja-AI FastAPI Backend
Smart Energy Management System for households with solar and smart meters.
"""

import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv

from backend.services.energy_service import get_live_energy
from backend.model.demand_forecast import get_next_day_demand_forecast
from backend.model.solar_forecast import get_next_day_solar_forecast
from backend.optimizer.scheduler import optimize_schedule
from backend.services.analytics_service import get_analytics_summary
from backend.services.assistant_service import get_supported_languages
from backend.services import user_service
from openai import AzureOpenAI

# 1. Load environment variables from .env
load_dotenv()

# 2. Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# 5. System prompt for the assistant
ASSISTANT_SYSTEM_PROMPT = (
    "You are a multilingual AI voice assistant.\n"
    "- Answer user questions naturally and clearly.\n"
    "- Support multiple Indian languages including Hindi, Telugu, Tamil, Bengali, Urdu, Marathi, Kannada, Malayalam, Gujarati, and Hinglish.\n"
    "- Always respond in the same language as the user input.\n"
    "- Keep responses short, conversational, and helpful.\n"
    "- Do not mention that you are an AI model.\n"
    "- Do not use technical jargon unless necessary."
)


def _profile_to_assistant_context(profile: Optional[Dict[str, Any]]) -> str:
    if not profile:
        return ""
    parts: List[str] = []
    if profile.get("state"):
        parts.append(f"State/region: {profile['state']}.")
    house = profile.get("house") or {}
    if house.get("type") or house.get("rooms") or house.get("people"):
        parts.append(
            f"Home: {house.get('type', 'unknown type')}, "
            f"{house.get('rooms', '?')} rooms, {house.get('people', '?')} people."
        )
    details = profile.get("applianceDetails") or []
    if isinstance(details, list) and details:
        bits = []
        for d in details:
            if not isinstance(d, dict) or not d.get("name"):
                continue
            bits.append(
                f"{d.get('name')} ×{d.get('count', 1)} (~{d.get('hours', 0)} h/day)"
            )
        if bits:
            parts.append("Appliances: " + "; ".join(bits))
    elif profile.get("appliances"):
        parts.append(
            "Appliances: " + ", ".join(str(a) for a in profile["appliances"])
        )
    bill = profile.get("bill")
    if bill not in (None, ""):
        parts.append(f"Approx. monthly electricity bill: ₹{bill}.")
    solar = profile.get("solar") or {}
    if solar.get("hasSolar"):
        nm = "yes" if solar.get("netMetering") else "no"
        parts.append(
            f"Solar: {solar.get('capacity', '?')} kW installed, net metering: {nm}."
        )
    if profile.get("usagePattern"):
        parts.append(f"Typical usage: {profile['usagePattern']}.")
    if profile.get("goal"):
        parts.append(f"User priority: {profile['goal']}.")
    if not parts:
        return ""
    return (
        "Household context (use when relevant; keep replies short):\n- "
        + "\n- ".join(parts)
    )


# 4. Azure OpenAI assistant function
def get_ai_response(
    user_query: str,
    language: str = "en",
    appliances: Optional[List[str]] = None,
    extra_context: Optional[str] = None,
) -> str:
    try:
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        lang = (language or "en").strip() or "en"
        ctx_bits = [
            f"Preferred response language code: {lang} (match the user's message language when possible)."
        ]
        if extra_context:
            ctx_bits.append(extra_context)
        elif appliances:
            ctx_bits.append(
                "User's registered appliances: "
                + ", ".join(str(a) for a in appliances)
                + ". Mention these only when relevant; keep answers concise."
            )
        system_content = ASSISTANT_SYSTEM_PROMPT + "\n" + "\n".join(ctx_bits)
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_query}
            ],
            max_tokens=256,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Azure OpenAI API Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Sorry, I couldn't process that. Please try again."


app = FastAPI(title="GramUrja-AI API", version="1.0.0")

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def home():
    return FileResponse("frontend/index.html")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExecuteCommandRequest(BaseModel):
    device: str
    action: str

# -------------------------
# Health / Home
# -------------------------


@app.get("/")
def home():
    return {"message": "GramUrja-AI Backend Running"}


# -------------------------
# Live Energy
# -------------------------
@app.get("/energy/live")
def live_energy():
    """Returns live home energy state (simulated from smart_meter + IoT variation)."""
    return get_live_energy()


# -------------------------
# Energy Forecast
# -------------------------
@app.get("/energy/forecast")
def energy_forecast():
    """Returns next-day demand and solar forecast."""
    demand_data = get_next_day_demand_forecast()
    solar_data = get_next_day_solar_forecast()
    return {
        "predicted_demand_kw": demand_data["predicted_avg_demand_kw"],
        "predicted_solar_kw": solar_data["predicted_peak_solar_kw"],
        "predicted_daily_demand_kwh": demand_data["predicted_daily_demand_kwh"],
        "predicted_solar_kwh": solar_data["predicted_solar_kwh"],
    }


# -------------------------
# Smart Schedule
# -------------------------
@app.get("/schedule/optimize")
def schedule_optimize():
    """Returns recommended appliance schedule based on solar and tariffs."""
    return optimize_schedule()


# -------------------------
# Analytics
# -------------------------
@app.get("/analytics/summary")
def analytics_summary():
    """Returns daily consumption, monthly cost estimate, top appliance."""
    return get_analytics_summary()


# -------------------------
# AI Assistant
# -------------------------
@app.post("/assistant/query")
async def assistant_query(request: Request):
    data = await request.json()
    user_query = data.get("message", "")
    profile = user_service.get_user_profile()
    language = data.get("language") or (profile or {}).get("language") or "en"
    appliances = data.get("appliances")
    if appliances is None and profile:
        appliances = profile.get("appliances")
    profile_ctx = _profile_to_assistant_context(profile)
    body_apps = data.get("appliances")
    if body_apps and isinstance(body_apps, list):
        extras = ", ".join(str(a) for a in body_apps)
        profile_ctx = (profile_ctx + "\n- Assistant UI appliance focus: " + extras) if profile_ctx else (
            "Household context:\n- Assistant UI appliance focus: " + extras
        )
    use_extra = bool(profile_ctx)
    response = get_ai_response(
        user_query,
        language=language,
        appliances=None if use_extra else appliances,
        extra_context=profile_ctx if use_extra else None,
    )
    return {"response": response}


@app.get("/assistant/languages")
def assistant_languages():
    """Returns supported languages (English + 10 Indian languages)."""
    return {"languages": get_supported_languages()}


# -------------------------
# User onboarding / profile
# -------------------------
@app.post("/user/onboard")
async def user_onboard(request: Request):
    body = await request.json()
    user_service.save_user_profile(body)
    profile = user_service.get_user_profile()
    return {"ok": True, "profile": profile}


@app.get("/user/profile")
def user_profile():
    return user_service.get_user_profile()


# -------------------------
# Tariff Prices (optional, for frontend)
# -------------------------
@app.get("/tariff/prices")
def tariff_prices():
    """Returns hourly tariff prices."""
    import pandas as pd
    from pathlib import Path
    path = Path(__file__).resolve().parent / "data" / "tariffs.csv"
    df = pd.read_csv(path)
    return {"tariffs": df[["hour", "price_per_kwh"]].to_dict(orient="records")}


# -------------------------
# AI Recommendation & IoT Command Simulation
# -------------------------


def send_command_to_iot(device: str, action: str) -> dict:
    """
    Simulate sending a command to an IoT device.

    Future implementation:
    - send command to Azure IoT Hub
    - using cloud-to-device messaging
    """
    # For now we just simulate success.
    return {
        "status": "success",
        "message": f"Command sent to device {device} with action '{action}'",
        "device": device,
        "action": action,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/ai-recommendation")
def ai_recommendation():
    """
    Returns a simulated AI recommendation for energy optimization.
    """
    # Static example for prototype; in real system this would be dynamic.
    return {
        "id": 1,
        "alert": True,
        "device": "AC",
        "action": "turn_off",
        "reason": "AC idle during peak tariff hours",
        "estimated_savings": "₹18",
    }


@app.post("/execute-command")
def execute_command(cmd: ExecuteCommandRequest):
    """
    Execute an IoT command (simulated) for a given device and action.
    """
    result = send_command_to_iot(cmd.device, cmd.action)
    # Match the expected frontend contract
    return {
        "status": result.get("status", "success"),
        "message": result.get("message", f"Command sent to device {cmd.device}"),
    }
