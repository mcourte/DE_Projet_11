import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.data_collection.open_agenda_client import fetch_events, save_raw_events
from src.data_collection.preprocessor import preprocess
from src.vectorstore.faiss_store import build_index

load_dotenv()


def main():
    city = os.getenv("TARGET_CITY", "Rennes")
    region = os.getenv("TARGET_REGION", "Bretagne")

    print(f"Étape 1/3 — Collecte des événements ({city}, {region})...")
    events = fetch_events(city=city, region=region)
    save_raw_events(events)

    print("\nÉtape 2/3 — Nettoyage des données...")
    df_clean_events = preprocess()

    print("\nÉtape 3/3 — Construction de l'index FAISS...")
    build_index(df_clean_events)

    print("\nBase vectorielle construite avec succès.")


if __name__ == "__main__":
    main()
