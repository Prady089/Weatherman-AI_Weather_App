#!/usr/bin/env python3
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# ================= CONFIG =================
LAT = float(os.getenv("LAT", "33.1546624"))
LON = float(os.getenv("LON", "-96.7180288"))
CITY = os.getenv("CITY", "McKinney")
TZ = ZoneInfo(os.getenv("TZ", "America/Chicago"))
UNITS = "metric"  # Celsius

OW_KEY = os.getenv("OPENWEATHER_API_KEY")
if not OW_KEY:
    raise RuntimeError("OPENWEATHER_API_KEY missing")

# Time blocks
BLOCKS = {
    "Morning 🌅": range(5, 11),
    "Noon 🌞": range(11, 16),
    "Evening 🌆": range(16, 20),
    "Night 🌙": range(20, 24),
}

# ================= HELPERS =================
def temp_range(vals):
    if not vals:
        return "--"
    lo, hi = round(min(vals)), round(max(vals))
    return f"{lo}–{hi}°" if lo != hi else f"{lo}°"

# ================= FETCH =================
url = (
    "https://api.openweathermap.org/data/3.0/onecall"
    f"?lat={LAT}&lon={LON}&exclude=minutely,daily&units={UNITS}&appid={OW_KEY}"
)

data = requests.get(url, timeout=20).json()
hourly = data["hourly"][:24]
current = data["current"]

# ================= VALUES =================
now = round(current["temp"])
desc = current["weather"][0]["description"].capitalize()
humidity = current["humidity"]
wind = f'{round(current["wind_speed"])} km/h'
temps = [h["temp"] for h in hourly]
high, low = round(max(temps)), round(min(temps))
rain = round(100 * max(h.get("pop", 0) for h in hourly))
date_str = datetime.now(TZ).strftime("%A, %B %d")

# ================= BLOCKS =================
block_vals = {}
for name, hours in BLOCKS.items():
    vals = [
        h["temp"]
        for h in hourly
        if datetime.fromtimestamp(h["dt"], TZ).hour in hours
    ]
    block_vals[name] = temp_range(vals)

# ================= HTML =================
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Today's Weather</title>
<style>
body {{
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  background: linear-gradient(180deg, #3a7bd5, #00d2ff);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}}
.card {{
  background: #0f2a44;
  color: #fff;
  border-radius: 24px;
  padding: 20px;
  width: 90%;
  max-width: 380px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}}
.header h1 {{ margin: 0; font-size: 20px; }}
.header p {{ margin: 0; opacity: 0.8; }}
.main {{ display: flex; align-items: center; margin: 20px 0; }}
.icon {{ font-size: 56px; margin-right: 16px; }}
.temp {{ font-size: 56px; font-weight: bold; }}
.desc {{ opacity: 0.85; }}
.row {{
  display: flex;
  justify-content: space-between;
  background: #0b2036;
  padding: 10px 14px;
  border-radius: 14px;
  margin-bottom: 10px;
}}
.blocks {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}}
.block {{
  background: #0b2036;
  padding: 10px;
  border-radius: 14px;
  text-align: center;
}}
</style>
</head>

<body>
<div class="card">
  <div class="header">
    <h1>{CITY}</h1>
    <p>{date_str}</p>
  </div>

  <div class="main">
    <div class="icon">🌤️</div>
    <div>
      <div class="temp">{now}°</div>
      <div class="desc">{desc}</div>
    </div>
  </div>

  <div class="row">
    <div>⬆ {high}°</div>
    <div>⬇ {low}°</div>
  </div>

  <div class="row">
    <div>💧 {humidity}%</div>
    <div>🌬 {wind}</div>
    <div>🌧 {rain}%</div>
  </div>

  <div class="blocks">
    {''.join(f'<div class="block">{k}<br>{v}</div>' for k, v in block_vals.items())}
  </div>
</div>
</body>
</html>
"""

os.makedirs("docs", exist_ok=True)
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ docs/index.html generated")
