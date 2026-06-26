import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OPEN_AGENDA_API_KEY = os.getenv("OPEN_AGENDA_API_KEY")
BASE_URL = "https://api.openagenda.com/v2"


def fetch_events(city: str, region: str, max_pages: int = 100) -> list:
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    params = {
        "key": OPEN_AGENDA_API_KEY,
        "size": 100,
        "city[]": city,
        "after[timings][gte]": one_year_ago,
        "lang": "fr",
    }

    events = []
    for page in range(max_pages):
        params["offset"] = page * 100
        response = requests.get(f"{BASE_URL}/events", params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        batch = data.get("events", [])
        if not batch:
            break
        events.extend(batch)
        print(f"Page {page + 1} — {len(batch)} événements récupérés")

    print(f"\nTotal : {len(events)} événements")
    return events


def save_raw_events(events: list, output_path: str = "data/raw/events.json") -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print(f"{len(events)} événements sauvegardés → {output_path}")
