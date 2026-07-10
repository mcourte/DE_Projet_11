import json
import logging
import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def load_raw_events(path: str = "data/raw/events.json") -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_within_one_year(event: dict) -> bool:
    cutoff = datetime.now() - timedelta(days=365)
    for key in ("firstTiming", "nextTiming", "lastTiming"):
        begin_str = (event.get(key) or {}).get("begin", "")
        if not begin_str:
            continue
        try:
            begin = datetime.fromisoformat(begin_str.replace("Z", "+00:00"))
            if begin.replace(tzinfo=None) >= cutoff:
                return True
        except ValueError:
            continue
    return False


def filter_recent_events(raw_events: list) -> list:
    recent_events = [e for e in raw_events if is_within_one_year(e)]
    logger.info(f"{len(recent_events)}/{len(raw_events)} événements conservés après filtre temporel (<1 an)")
    return recent_events


def extract_fields(event: dict) -> dict:
    title = (
        event.get("title", {}).get("fr", "")
        or event.get("title", {}).get("en", "")
    )
    description = (
        event.get("longDescription", {}).get("fr", "")
        or event.get("description", {}).get("fr", "")
        or ""
    )
    description = description.encode("utf-8", errors="ignore").decode("utf-8")

    location = event.get("location", {})
    first_timing = event.get("firstTiming", {})
    slug = event.get("slug", "")
    agenda_uid = event.get("originAgenda", {}).get("uid", "")
    url = f"https://openagenda.com/agendas/{agenda_uid}/events/{slug}" if slug else ""

    return {
        "id": event.get("uid", ""),
        "title": title,
        "description": description,
        "city": location.get("city", ""),
        "address": location.get("address", ""),
        "first_date": first_timing.get("begin", ""),
        "url": url,
    }


def build_dataframe(recent_events: list) -> pd.DataFrame:
    extracted_fields = [extract_fields(e) for e in recent_events]
    return pd.DataFrame(extracted_fields)


TARGET_CITY = os.getenv("TARGET_CITY", "")


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df_cleaned = df.dropna(subset=["title", "description"])
    df_cleaned = df_cleaned[df_cleaned["description"].str.strip().str.len() >= 20]
    df_cleaned = df_cleaned[df_cleaned["city"].str.strip() != ""]
    if TARGET_CITY:
        df_cleaned = df_cleaned[
            df_cleaned["city"].str.lower() == TARGET_CITY.lower()
        ]
        logger.info(f"Filtre ville '{TARGET_CITY}' appliqué : {len(df_cleaned)} événements")
    logger.info(f"{len(df_cleaned)} événements après nettoyage")
    return df_cleaned


def save_events(df: pd.DataFrame, output_path: str = "data/processed/events_clean.csv") -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"{len(df)} événements sauvegardés → {output_path}")


def preprocess(
    raw_path: str = "data/raw/events.json",
    output_path: str = "data/processed/events_clean.csv",
) -> pd.DataFrame:
    raw_events = load_raw_events(raw_path)
    logger.info(f"{len(raw_events)} événements bruts chargés")

    recent_events = filter_recent_events(raw_events)
    df_events = build_dataframe(recent_events)
    df_clean_events = clean_dataframe(df_events)
    save_events(df_clean_events, output_path)

    return df_clean_events
