import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


def load_raw_events(path: str = "data/raw/events.json") -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_within_one_year(event: dict) -> bool:
    cutoff = datetime.now() - timedelta(days=365)
    for timing in event.get("timings", []):
        begin_str = timing.get("begin", "")
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
    print(f"{len(recent_events)}/{len(raw_events)} événements conservés après filtre temporel (<1 an)")
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
    timings = event.get("timings", [])

    return {
        "id": event.get("uid", ""),
        "title": title,
        "description": description,
        "city": location.get("city", ""),
        "address": location.get("address", ""),
        "first_date": timings[0].get("begin", "") if timings else "",
        "url": event.get("canonicalUrl", ""),
    }


def build_dataframe(recent_events: list) -> pd.DataFrame:
    extracted_fields = [extract_fields(e) for e in recent_events]
    return pd.DataFrame(extracted_fields)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df_cleaned = df.dropna(subset=["title", "description"])
    df_cleaned = df_cleaned[df_cleaned["description"].str.strip().str.len() >= 20]
    df_cleaned = df_cleaned[df_cleaned["city"].str.strip() != ""]
    print(f"{len(df_cleaned)} événements après nettoyage (descriptions vides, villes manquantes)")
    return df_cleaned


def save_events(df: pd.DataFrame, output_path: str = "data/processed/events_clean.csv") -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"{len(df)} événements sauvegardés → {output_path}")


def preprocess(
    raw_path: str = "data/raw/events.json",
    output_path: str = "data/processed/events_clean.csv",
) -> pd.DataFrame:
    raw_events = load_raw_events(raw_path)
    print(f"{len(raw_events)} événements bruts chargés")

    recent_events = filter_recent_events(raw_events)
    df_events = build_dataframe(recent_events)
    df_clean_events = clean_dataframe(df_events)
    save_events(df_clean_events, output_path)

    return df_clean_events
