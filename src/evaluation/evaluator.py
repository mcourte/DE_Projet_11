import json
import logging
import os
from langchain_mistralai import ChatMistralAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

EVAL_PROMPT = """Tu es un juge impartial chargé de comparer deux réponses.
Réponds uniquement par OUI si les deux réponses ont le même sens et les mêmes informations essentielles,
ou par NON si elles diffèrent sur un point important.

Réponse attendue : {expected}
Réponse obtenue : {actual}

Verdict (OUI ou NON) :"""


def load_qa_dataset(qa_dataset_path: str) -> list:
    with open(qa_dataset_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_judge() -> ChatMistralAI:
    return ChatMistralAI(
        model="mistral-large-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0,
    )


def _query_rag_chain(chain: RetrievalQA, question: str) -> str:
    result = chain({"query": question})
    return result["result"]


def _judge_single_answer(expected: str, actual: str, judge: ChatMistralAI) -> bool:
    verdict = judge.invoke(
        EVAL_PROMPT.format(expected=expected, actual=actual)
    ).content.strip().upper()
    return verdict == "OUI"


def _evaluate_single_item(item: dict, chain: RetrievalQA, judge: ChatMistralAI) -> dict:
    actual = _query_rag_chain(chain, item["question"])
    is_correct = _judge_single_answer(item["expected_answer"], actual, judge)
    status = "OK" if is_correct else "KO"
    logger.info(f"[{status}] {item['question'][:60]}...")
    return {
        "question": item["question"],
        "expected": item["expected_answer"],
        "actual": actual,
        "correct": is_correct,
    }


def _compute_score(results: list) -> float:
    return sum(1 for r in results if r["correct"]) / len(results) if results else 0.0


def _log_score(results: list, score: float) -> None:
    logger.info("=== Résultat évaluation RAG ===")
    logger.info(f"Score : {sum(r['correct'] for r in results)}/{len(results)} ({score:.1%})")


def evaluate(
    chain: RetrievalQA,
    qa_dataset_path: str = "data/processed/qa_dataset.json",
) -> dict:
    dataset = load_qa_dataset(qa_dataset_path)
    judge = _build_judge()

    results = [_evaluate_single_item(item, chain, judge) for item in dataset]

    score = _compute_score(results)
    _log_score(results, score)

    return {"score": score, "details": results}
