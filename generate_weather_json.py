#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# =========================
# CONFIG (Celsius)
# =========================
LAT = float(os.getenv("LAT", "33.1546624"))
LON = float(os.getenv("LON", "-96.7180288"))
CITY = os.getenv("CITY", "McKinney")
TZ = ZoneInfo(os.getenv("TZ", "America/Chicago"))
UNITS = "metric"  # Celsius

OUT_FILE = "docs/weather.json"

# Time blocks
BLOCKS = {
    "morning": range(5, 11),   # 5–10
    "noon": range(11, 16),     # 11–15
    "evening": range(16, 20),  # 16–19
    "night": range(20, 24),    # 20–23
}

OW_KEY = os.getenv("OPENWEATHER_API_KEY")
if not OW_KEY:
    raise RuntimeError("OPENWEATHER_API_KEY missing")

# =========================
# HELPERS
# =========================
def en_range(values):
    if not values:
        return "--"
    lo = round(min(values))
    hi = round(max(values))
    return f"{lo}–{hi}°" if lo != hi else f"{lo}°"

# =========================
# FETCH DATA
# =========================
url = (
    "https://api.openweathermap.org/data/3.0/onecall"
    f"?lat={LAT}&lon={LON}"
    f"&exclude=minutely,daily"
    f"&units={UNITS}"
    f"&appid={OW_KEY}"
)

resp = requests.get(url, timeout=20)
data = resp.json()

if resp.status_code != 200 or "hourly" not in data:
    raise RuntimeError(f"OpenWeather error: {data}")

current = data["current"]
hourly = data["hourly"][:24]

# =========================
# CORE VALUES
# =========================
now_temp = round(current["temp"])
desc = current["weather"][0]["description"].capitalize()
humidity = current["humidity"]
wind = f'{round(current["wind_speed"])} km/h'

temps24 = [h["temp"] for h in hourly]
high = round(max(temps24))
low = round(min(temps24))

pops = [h.get("pop", 0) for h in hourly]
rain_pct = round(100 * max(pops)) if pops else 0

# =========================
# TIME BLOCK RANGES
# =========================
blocks = {k: [] for k in BLOCKS}

for h in hourly:
    ts = datetime.fromtimestamp(h["dt"], TZ)
    for name, hours in BLOCKS.items():
        if ts.hour in hours:
            blocks[name].append(h["temp"])

block_ranges = {k: en_range(v) for k, v in blocks.items()}

# =========================
# FINAL PAYLOAD
# =========================
payload = {
    "city": CITY,
    "date": datetime.now(TZ).strftime("%A, %B %d"),
    "now": now_temp,
    "desc": desc,
    "high": high,
    "low": low,
    "humidity": humidity,
    "wind": wind,
    "rain": rain_pct,
    "blocks": block_ranges,
}

os.makedirs("docs", exist_ok=True)
with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

print("✅ Generated docs/weather.json")
