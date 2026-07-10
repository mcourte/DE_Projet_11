import requests
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPEN_AGENDA_API_KEY = os.getenv("OPEN_AGENDA_API_KEY")
BASE_URL = "https://api.openagenda.com/v2"


def _find_agenda_uids(city: str) -> list[int]:
    params = {"key": OPEN_AGENDA_API_KEY, "city[]": city, "size": 5, "lang": "fr"}
    response = requests.get(f"{BASE_URL}/agendas", params=params, timeout=30)
    logger.info(f"Recherche agendas — status: {response.status_code}")
    logger.info(f"Réponse brute: {response.text[:500]}")
    response.raise_for_status()
    agendas = response.json().get("agendas", [])
    uids = [a["uid"] for a in agendas]
    logger.info(f"Agendas trouvés pour '{city}': {uids}")
    return uids


def _fetch_events_for_agenda(uid: int, city: str, max_pages: int) -> list:
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%S")
    url = f"{BASE_URL}/agendas/{uid}/events"
    params = {
        "key": OPEN_AGENDA_API_KEY,
        "size": 100,
        "timings[gte]": one_year_ago,
        "lang": "fr",
    }
    events = []
    for page in range(max_pages):
        params["offset"] = page * 100
        response = requests.get(url, params=params, timeout=30)
        logger.debug(f"Agenda {uid} page {page} — status {response.status_code}")
        response.raise_for_status()
        batch = response.json().get("events", [])
        if not batch:
            break
        events.extend(batch)
        logger.info(f"Agenda {uid} — page {page + 1} : {len(batch)} événements")
    return events


def fetch_events(city: str, region: str, max_pages: int = 100) -> list:
    agenda_uid_env = os.getenv("OPEN_AGENDA_UID")
    if agenda_uid_env:
        uids = [int(agenda_uid_env)]
        logger.info(f"Utilisation de l'agenda UID={agenda_uid_env} (depuis .env)")
    else:
        uids = _find_agenda_uids(city)
        if not uids:
            logger.error(
                f"Aucun agenda trouvé pour '{city}'. "
                "Définissez OPEN_AGENDA_UID dans votre .env avec l'UID d'un agenda openagenda.com."
            )
            return []

    all_events = []
    for uid in uids:
        all_events.extend(_fetch_events_for_agenda(uid, city, max_pages))

    logger.info(f"Total : {len(all_events)} événements")
    return all_events


def save_raw_events(events: list, output_path: str = "data/raw/events.json") -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    logger.info(f"{len(events)} événements sauvegardés → {output_path}")
