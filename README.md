# Shah Family NYC Guide 🗽

A personalized, interactive travel guide for the Shah family's NYC trips. Built with Flask, Leaflet.js, and OpenAI.

## Features

- **📋 List View** — Filter 47+ curated spots by category (Food, Sightseeing, Broadway), subcategory (Pizza, Indian, Bagels, etc.), and distance
- **🗺️ Map View** — Interactive Leaflet map with color-coded pins, Vishal's Picks overlays, and live user location
- **💬 Chat View** — AI concierge powered by GPT-4o-mini, grounded in all spot data and your live GPS location
- **⭐ Vishal's Picks** — Gold-starred personal recommendations with insider tips
- **📍 Geolocation** — Sort by nearest, live walking distances, one-tap Google Maps directions
- **🌙 Dark Mode** — Auto-detects system preference

## Tech Stack

- **Backend:** Python/Flask + Gunicorn
- **Frontend:** Vanilla JS, Leaflet.js + OpenStreetMap tiles
- **AI:** OpenAI GPT-4o-mini for chat
- **Deployment:** Fly.io (Docker, auto-stop enabled)

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your-key-here
python app.py
```

## Deployment

Deployed on Fly.io:

```bash
fly deploy
```

The OpenAI API key is set as a Fly secret:

```bash
fly secrets set OPENAI_API_KEY=your-key-here
```

## Live

**https://shah-nyc-guide.fly.dev/**

---

Made with ❤️ by DootDoot ⚡ for the Shah Family
