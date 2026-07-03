# =============================================================================
# FICHIER : test_data_pipeline.py
# Rôle    : vérifier que les données collectées et traitées sont conformes
# =============================================================================
#
# Ces tests s'exécutent avec pytest :
#   pytest tests/ -v
#
# Ils vérifient deux choses importantes :
#   1. La FRAÎCHEUR des données : tous les événements doivent dater de < 1 an
#   2. Le FILTRE GÉOGRAPHIQUE : tous les événements doivent être dans la bonne ville
#
# Important : ces tests nécessitent que le pipeline ait déjà tourné
# (data/raw/events.json et data/processed/events_clean.csv doivent exister).
#
# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 1 — Les imports et configuration
# ─────────────────────────────────────────────────────────────────────────────
# Importe : json, os, pytest, datetime, timedelta, load_dotenv
#
# Appelle load_dotenv() pour charger le .env.
# Récupère TARGET_CITY = os.getenv("TARGET_CITY", "Paris")
#
# Définis les chemins en constantes :
#   RAW_PATH       = "data/raw/events.json"
#   PROCESSED_PATH = "data/processed/events_clean.csv"
#
# ─────────────────────────────────────────────────────────────────────────────
# CLASSE TestDataFreshness — Tests sur la fraîcheur des données
# ─────────────────────────────────────────────────────────────────────────────
#
# test_raw_file_exists :
#   Vérifie que data/raw/events.json existe.
#   Utilise os.path.exists() + assert.
#
# test_processed_file_exists :
#   Vérifie que data/processed/events_clean.csv existe.
#
# test_all_events_within_one_year :
#   Charge les événements bruts depuis RAW_PATH.
#   Calcule la date limite : datetime.now() - timedelta(days=365)
#   Pour chaque événement, vérifie qu'au moins un timing["begin"] >= date limite.
#   Si un événement ne passe pas, ajoute son uid à une liste violations.
#   L'assertion finale : assert len(violations) == 0
#   (avec un message qui liste les uid fautifs)
#
# test_processed_events_have_required_columns :
#   Charge le CSV avec pandas.
#   Vérifie que les colonnes {"id","title","description","city","first_date"}
#   sont toutes présentes dans df.columns.
#
# test_no_empty_descriptions :
#   Charge le CSV.
#   Filtre les lignes où description.str.strip() == "".
#   Vérifie que ce DataFrame filtré est vide (longueur == 0).
#
# ─────────────────────────────────────────────────────────────────────────────
# CLASSE TestGeographicFilter — Tests sur le filtre géographique
# ─────────────────────────────────────────────────────────────────────────────
#
# test_events_match_target_city :
#   Charge le CSV.
#   Filtre les lignes où la colonne "city" ne contient PAS TARGET_CITY
#   (utilise str.lower().str.contains() pour une comparaison insensible à la casse).
#   Vérifie que ce DataFrame filtré est vide.
#   Message d'erreur : préciser combien d'événements ne correspondent pas.
#
# test_minimum_event_count :
#   Charge le CSV.
#   Vérifie qu'il y a au moins 10 événements.
#   Si len(df) < 10, le test échoue avec un message explicatif.
