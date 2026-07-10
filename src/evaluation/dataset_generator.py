import json
import logging
import os
import pandas as pd
from langchain_mistralai import ChatMistralAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GENERATION_PROMPT = """Tu es un testeur d'application. À partir de l'événement culturel suivant,
génère une question naturelle qu'un utilisateur pourrait poser à un chatbot,
ainsi que la réponse précise attendue.

Événement :
- Titre : {title}
- Description : {description}
- Ville : {city}
- Date : {first_date}

Réponds uniquement en JSON valide, sans texte autour :
{{"question": "...", "expected_answer": "..."}}"""


def _build_llm() -> ChatMistralAI:
    return ChatMistralAI(
        model="mistral-large-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.7,
    )


def _build_prompt() -> PromptTemplate:
    return PromptTemplate(
        template=GENERATION_PROMPT,
        input_variables=["title", "description", "city", "first_date"],
    )


def _sample_events(df_clean_events: pd.DataFrame, n_samples: int) -> pd.DataFrame:
    return df_clean_events.sample(min(n_samples, len(df_clean_events)))


def _generate_single_pair(row: pd.Series, llm: ChatMistralAI, prompt: PromptTemplate) -> dict | None:
    formatted_prompt = prompt.format(
        title=row["title"],
        description=str(row["description"])[:400],
        city=row["city"],
        first_date=row["first_date"],
    )
    try:
        response = llm.invoke(formatted_prompt)
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1].replace("json", "").strip()
        qa = json.loads(content)
        qa["source_event_id"] = row["id"]
        logger.info(f"Q/R générée : {qa['question'][:60]}...")
        return qa
    except (json.JSONDecodeError, IndexError):
        return None


def save_qa_pairs(qa_pairs: list, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
    logger.info(f"{len(qa_pairs)} paires Q/R sauvegardées → {output_path}")


def generate_qa_pairs(
    df_clean_events: pd.DataFrame,
    n_samples: int = 20,
    output_path: str = "data/processed/qa_dataset.json",
) -> list:
    llm = _build_llm()
    prompt = _build_prompt()
    sample = _sample_events(df_clean_events, n_samples)

    qa_pairs = [
        pair
        for _, row in sample.iterrows()
        if (pair := _generate_single_pair(row, llm, prompt)) is not None
    ]

    save_qa_pairs(qa_pairs, output_path)
    return qa_pairs
