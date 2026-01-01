🌦️ Weatherman — Smart Weather Alerts & Daily Dashboard

Weatherman is a personal, automation-driven weather alert system that delivers:

📱 Smart push notifications (rain + cold alerts)

🧠 Noise-free alerts based on threshold crossings

🖼️ A static, mobile-friendly daily weather dashboard

🔐 Secure API usage (no keys exposed in the browser)

⚙️ Fully automated via GitHub Actions

This project is designed to be reliable, minimal, and human-centric — not a full weather app, but a signal-driven assistant.

✨ Key Features
🌧️ Rain Alerts

Notifies when rain is expected soon

Fires once per rain event

Avoids repeat notifications

❄️ Cold Weather Alerts (Smart Thresholds)

Alerts trigger only when temperature crosses below a threshold:

Threshold	Alert
≤ 15°C	🧥 Cool weather
≤ 10°C	❄️ Cold
≤ 5°C	🧊 Very cold
≤ 0°C	🥶 Freezing (critical)

✔ Uses feels-like temperature
✔ Sends only one alert per crossing
✔ Prevents alert spam

🌙 Quiet Hours Support

Quiet hours: 11 PM – 6 AM

Informational alerts are suppressed

Freezing alerts always break through

This ensures alerts remain trustworthy and non-intrusive.

🖼️ Daily Weather Dashboard

Generated once every morning

Fully static HTML (no JS fetch, no caching issues)

Optimized for iPhone lock-screen viewing

Linked directly from push notifications

Shows:

Current temperature

Feels-like temperature

High / Low

Rain probability

Wind & humidity

Morning / Noon / Evening / Night ranges

🧠 Architecture Overview
OpenWeather API
      ↓
GitHub Actions (cron or manual)
      ↓
Python scripts
      ↓
Static HTML dashboard (docs/index.html)
      ↓
GitHub Pages
      ↓
Pushover notifications → tap to open dashboard


No live polling. No browser-side API calls.

📁 Project Structure
/
├── docs/
│   └── index.html            # Generated daily dashboard
├── generate_index_html.py    # Builds the static dashboard
├── rain_alert.py             # Rain + cold alert engine
└── .github/workflows/
    └── generate_dashboard.yml

🔐 Required Secrets (GitHub Actions)

Add these in:

Repo → Settings → Secrets → Actions

Name	Description
OPENWEATHER_API_KEY	OpenWeather API key
PUSHOVER_TOKEN	Pushover application token
PUSHOVER_USER	Pushover user key
⚙️ Configuration (Environment Variables)

Set via GitHub Actions:

CITY: McKinney
LAT: "33.1546624"
LON: "-96.7180288"
TZ: America/Chicago


Units are fixed to Celsius.

▶️ How It Runs
Daily Dashboard

Runs automatically every morning (cron)

Can also be triggered manually from GitHub Actions

Generates docs/index.html

Deployed via GitHub Pages

Alerts

Intended to run every 10–15 minutes

Sends notifications only when something changes

Uses state tracking to avoid duplicates

📱 Notification Experience

Example cold alert:

🥶 Freezing Alert

Current: -2°C
Feels like: -6°C

Risk of frost or icy surfaces.


Example daily notification:

🌤️ Today – McKinney
24°C Clear
⬆ 27° ⬇ 17°

Open Weather Dashboard →

🎯 Design Principles

Signal over noise

Event-based alerts, not constant updates

Human-centric data (feels-like temperature)

Static over dynamic for reliability

Automation-first

🛠️ Possible Enhancements

Forecast-based cold alerts

Commute-aware alert timing

Weekend vs weekday behavior

7-day static forecast on dashboard

UI refinement via Figma

Additional alert channels (email, Slack)

📜 License

Personal project — feel free to fork, adapt, and extend.

🙌 Acknowledgements

OpenWeather API

Pushover Notifications

GitHub Actions & Pages
