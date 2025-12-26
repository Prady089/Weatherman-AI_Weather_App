import requests
from datetime import datetime

LAT = 33.1546624
LON = -96.7180288
UNITS = "metric"

OW_KEY = "${{ secrets.OPENWEATHER_API_KEY }}"
PUSH_TOKEN = "${{ secrets.PUSHOVER_TOKEN }}"
PUSH_USER = "${{ secrets.PUSHOVER_USER }}"

# Fetch weather
url = (
    f"https://api.openweathermap.org/data/3.0/onecall"
    f"?lat={LAT}&lon={LON}&exclude=minutely,daily&units={UNITS}&appid={OW_KEY}"
)
data = requests.get(url).json()

import sys

if "hourly" in data:
    hourly = data["hourly"][:24:3]
    print("Using One Call API hourly data")
else:
    print("One Call API failed, falling back to forecast API")
    print("Response was:", data)

    # 🔁 FALLBACK: 3-hour forecast API
    fallback_url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={LAT}&lon={LON}&units={UNITS}&appid={OW_KEY}"
    )

    fallback = requests.get(fallback_url).json()

    if "list" not in fallback:
        print("Fallback API also failed:", fallback)
        sys.exit(1)

    hourly = fallback["list"][:8]  # next 24 hours (3h blocks)

times = []
temps = []
rain_alerts = []

for h in hourly:
    time = datetime.fromtimestamp(h["dt"]).strftime("%-I%p")
    temp = f"{round(h['temp'])}°"
    times.append(time)
    temps.append(temp)

    # 🌧 Rain detection
    if "rain" in h:
        rain_alerts.append(f"🌧 {time}")

# Build message (lock-screen friendly)
message = (
    "🌤️ Today – McKinney\n\n"
    + " ".join(times) + "\n"
    + " ".join(temps)
)

# Add rain warning if any
if rain_alerts:
    message += "\n\n⚠️ Rain expected: " + ", ".join(rain_alerts)

# Send push
requests.post(
    "https://api.pushover.net/1/messages.json",
    data={
        "token": PUSH_TOKEN,
        "user": PUSH_USER,
        "title": "Daily Weather",
        "message": message,
        "priority": 0
    }
)
