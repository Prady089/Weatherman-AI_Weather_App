#!/usr/bin/env python3
import os
import sys
import requests
from datetime import datetime, timezone

# =========================
# CONFIG
# =========================
LAT = 33.1546624
LON = -96.7180288
UNITS = "metric"
TIMEZONE_NAME = "America/Chicago"

# =========================
# ENV VARS
# =========================
OW_KEY = os.getenv("OPENWEATHER_API_KEY")
PUSH_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSH_USER = os.getenv("PUSHOVER_USER")

print("🔍 Starting Weather Automation")

# Validate env vars
if not OW_KEY:
    print("❌ OPENWEATHER_API_KEY missing")
    sys.exit(1)
if not PUSH_TOKEN or not PUSH_USER:
    print("❌ Pushover credentials missing")
    sys.exit(1)

print(f"✅ OpenWeather key detected (ends with {OW_KEY[-4:]})")

# =========================
# HELPERS
# =========================
def http_get(url, label):
    print(f"\n➡️ Calling {label}")
    print(url)
    r = requests.get(url, timeout=20)
    print(f"⬅️ HTTP {r.status_code}")
    try:
        data = r.json()
    except Exception:
        print("❌ Response is not JSON")
        print(r.text)
        sys.exit(1)
    return r.status_code, data


def send_push(title, message, priority=0):
    print("📲 Sending push notification")
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
    print(f"📨 Pushover HTTP {r.status_code}")
    print(r.text)


# =========================
# STEP 1: TRY ONE CALL 3.0
# =========================
onecall_url = (
    "https://api.openweathermap.org/data/3.0/onecall"
    f"?lat={LAT}&lon={LON}"
    f"&exclude=minutely,daily"
    f"&units={UNITS}"
    f"&appid={OW_KEY}"
)

status, data = http_get(onecall_url, "One Call 3.0")

hourly = None
source = None

if status == 200 and "hourly" in data:
    hourly = data["hourly"]
    source = "onecall"
    print(f"✅ One Call hourly data received ({len(hourly)} points)")
else:
    print("⚠️ One Call API did not return hourly data")
    print("Payload:", data)

# =========================
# STEP 2: FALLBACK TO FORECAST
# =========================
if hourly is None:
    forecast_url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={LAT}&lon={LON}"
        f"&units={UNITS}"
        f"&appid={OW_KEY}"
    )

    status, data = http_get(forecast_url, "Forecast 3-hour API")

    if status != 200 or "list" not in data:
        print("❌ Forecast API also failed")
        print("Payload:", data)

        send_push(
            "Weather Automation FAILED",
            f"OpenWeather APIs failed.\n\nResponse:\n{data}",
            priority=1,
        )
        sys.exit(1)

    hourly = data["list"]
    source = "forecast"
    print(f"✅ Forecast data received ({len(hourly)} points)")

# =========================
# STEP 3: BUILD 3-HOUR TIMELINE
# =========================
print(f"🧠 Using data source: {source}")

slots = hourly[:8]  # next 24 hours (3-hour blocks)

times = []
temps = []
rain_times = []

for h in slots:
    ts = h["dt"]
    temp = round(h["temp"])
    time_str = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone().strftime("%-I%p")

    times.append(time_str)
    temps.append(f"{temp}°")

    if "rain" in h or (
        "weather" in h and any(w["main"].lower() == "rain" for w in h["weather"])
    ):
        rain_times.append(time_str)

# =========================
# STEP 4: FORMAT MESSAGE
# =========================
times_line = " ".join(f"{t:>4}" for t in times)
temps_line = " ".join(f"{t:>4}" for t in temps)

message = (
    "🌤️ Today – McKinney\n\n"
    f"{times_line}\n"
    f"{temps_line}"
)

if rain_times:
    message += "\n\n⚠️ Rain expected: " + ", ".join(rain_times)

message += f"\n\n(source: {source})"

# =========================
# STEP 5: SEND PUSH
# =========================
send_push("Daily Weather", message)

print("✅ Weather automation completed successfully")
