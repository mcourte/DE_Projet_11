import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

from dotenv import load_dotenv
from src.data_collection.open_agenda_client import fetch_events, save_raw_events
from src.data_collection.preprocessor import preprocess
from src.vectorstore.faiss_store import build_index

load_dotenv()


logger = logging.getLogger(__name__)


def main():
    city = os.getenv("TARGET_CITY", "Rennes")
    region = os.getenv("TARGET_REGION", "Bretagne")

    logger.info(f"Étape 1/3 — Collecte des événements ({city}, {region})...")
    events = fetch_events(city=city, region=region)
    save_raw_events(events)

    logger.info("Étape 2/3 — Nettoyage des données...")
    df_clean_events = preprocess()

    logger.info("Étape 3/3 — Construction de l'index FAISS...")
    build_index(df_clean_events)

    logger.info("Base vectorielle construite avec succès.")


if __name__ == "__main__":
    main()
