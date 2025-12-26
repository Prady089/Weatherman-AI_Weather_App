#!/usr/bin/env python3
import os
import sys
import json
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

LAT = float(os.getenv("LAT", "33.1546624"))
LON = float(os.getenv("LON", "-96.7180288"))
CITY = os.getenv("CITY", "McKinney")
UNITS = os.getenv("UNITS", "metric")
TZ = ZoneInfo(os.getenv("TZ", "America/Chicago"))

OW_KEY = os.getenv("OPENWEATHER_API_KEY")
PUSH_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSH_USER = os.getenv("PUSHOVER_USER")

STATE_PATH = os.getenv("RAIN_STATE_PATH", ".state/rain_state.json")

if not OW_KEY or not PUSH_TOKEN or not PUSH_USER:
    print("❌ Missing env vars.")
    sys.exit(1)

def send_push(title: str, message: str, priority: int = 1):
    r = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": PUSH_TOKEN,
            "user": PUSH_USER,
            "title": title,
            "message": message,
            "priority": priority,
        },
        timeout=20,
    )
    print("Pushover:", r.status_code, r.text)

def load_state():
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"last_alert_dt": None, "last_rain_start": None}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f)

def ow_onecall():
    url = (
        "https://api.openweathermap.org/data/3.0/onecall"
        f"?lat={LAT}&lon={LON}&exclude=daily&units={UNITS}&appid={OW_KEY}"
    )
    r = requests.get(url, timeout=20)
    data = r.json()
    if r.status_code != 200:
        raise RuntimeError(f"OpenWeather HTTP {r.status_code}: {data}")
    return data

def main():
    state = load_state()

    data = ow_onecall()
    now = datetime.now(TZ)

    # Detect imminent rain (prefer minutely if present)
    rain_start = None
    intensity = 0.0

    minutely = data.get("minutely", [])
    if minutely:
        # next 60 minutes
        for m in minutely[:60]:
            if m.get("precipitation", 0) and m["precipitation"] > 0:
                rain_start = datetime.fromtimestamp(m["dt"], TZ)
                intensity = float(m["precipitation"])
                break
    else:
        # fallback: hourly (next ~2 hours)
        for h in data.get("hourly", [])[:2]:
            pop = float(h.get("pop", 0) or 0)
            is_rain = any(w.get("main","").lower() == "rain" for w in h.get("weather", []))
            has_rain_obj = "rain" in h
            if has_rain_obj or (is_rain and pop >= 0.4):
                rain_start = datetime.fromtimestamp(h["dt"], TZ)
                intensity = float(h.get("rain", {}).get("1h", 0) or 0)
                break

    # Reset state if no rain soon
    if not rain_start:
        state["last_rain_start"] = None
        save_state(state)
        print("No imminent rain.")
        return

    # Prevent duplicate alerts: alert once per rain_start window
    last_rain_start = state.get("last_rain_start")
    if last_rain_start == rain_start.isoformat():
        print("Already alerted for this rain window.")
        return

    # Compose compact message
    start_str = rain_start.strftime("%-I:%M %p")
    soon_mins = max(0, int((rain_start - now).total_seconds() // 60))

    # Simple intensity label
    if intensity >= 2.5:
        level = "heavy"
    elif intensity >= 1.0:
        level = "moderate"
    elif intensity > 0:
        level = "light"
    else:
        level = "possible"

    msg = (
        f"🌧️ Rain Alert – {CITY}\n\n"
        f"Starts ~{start_str} ({soon_mins} min)\n"
        f"Intensity: {level}\n\n"
        f"🌂 If you’re heading out, take an umbrella."
    )

    send_push("Rain Alert", msg, priority=1)

    state["last_rain_start"] = rain_start.isoformat()
    save_state(state)

if __name__ == "__main__":
    main()
