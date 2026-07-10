import json
import os
import pytest
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

RAW_PATH = "data/raw/events.json"
PROCESSED_PATH = "data/processed/events_clean.csv"
TARGET_CITY = os.getenv("TARGET_CITY", "Rennes")


class TestDataFreshness:

    def test_raw_file_exists(self):
        assert os.path.exists(RAW_PATH), f"Fichier introuvable : {RAW_PATH}"

    def test_processed_file_exists(self):
        assert os.path.exists(PROCESSED_PATH), f"Fichier introuvable : {PROCESSED_PATH}"

    def test_all_events_within_one_year(self):
        with open(RAW_PATH, "r", encoding="utf-8") as f:
            raw_events = json.load(f)

        cutoff = datetime.now() - timedelta(days=365)
        violations = []

        for event in raw_events:
            has_recent_timing = False
            for key in ("firstTiming", "nextTiming", "lastTiming"):
                begin_str = (event.get(key) or {}).get("begin", "")
                if not begin_str:
                    continue
                try:
                    begin = datetime.fromisoformat(begin_str.replace("Z", "+00:00"))
                    if begin.replace(tzinfo=None) >= cutoff:
                        has_recent_timing = True
                        break
                except ValueError:
                    continue
            if not has_recent_timing:
                violations.append(event.get("uid", "unknown"))

        assert len(violations) == 0, (
            f"{len(violations)} événements dépassent la limite d'1 an : {violations[:5]}"
        )

    def test_processed_events_have_required_columns(self):
        df = pd.read_csv(PROCESSED_PATH)
        required_columns = {"id", "title", "description", "city", "first_date"}
        missing = required_columns - set(df.columns)
        assert len(missing) == 0, f"Colonnes manquantes : {missing}"

    def test_no_empty_descriptions(self):
        df = pd.read_csv(PROCESSED_PATH)
        empty = df[df["description"].str.strip() == ""]
        assert len(empty) == 0, f"{len(empty)} événements sans description."


class TestGeographicFilter:

    def test_events_match_target_city(self):
        df = pd.read_csv(PROCESSED_PATH)
        mismatches = df[~df["city"].str.lower().str.contains(TARGET_CITY.lower(), na=False)]
        assert len(mismatches) == 0, (
            f"{len(mismatches)} événements hors de {TARGET_CITY} : "
            f"{mismatches['city'].unique().tolist()[:5]}"
        )

    def test_minimum_event_count(self):
        df = pd.read_csv(PROCESSED_PATH)
        assert len(df) >= 10, (
            f"Seulement {len(df)} événements — vérifier le filtre géographique ou l'API."
        )
