import json
import os
from langchain_mistralai import ChatMistralAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

EVAL_PROMPT = """Tu es un juge impartial chargé de comparer deux réponses.
Réponds uniquement par OUI si les deux réponses ont le même sens et les mêmes informations essentielles,
ou par NON si elles diffèrent sur un point important.

Réponse attendue : {expected}
Réponse obtenue : {actual}

Verdict (OUI ou NON) :"""


def evaluate(
    chain: RetrievalQA,
    qa_dataset_path: str = "data/processed/qa_dataset.json",
) -> dict:
    with open(qa_dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    judge = ChatMistralAI(
        model="mistral-large-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0,
    )

    results = []
    for item in dataset:
        result = chain({"query": item["question"]})
        actual = result["result"]

        verdict = judge.invoke(
            EVAL_PROMPT.format(
                expected=item["expected_answer"],
                actual=actual,
            )
        ).content.strip().upper()

        is_correct = verdict == "OUI"
        results.append({
            "question": item["question"],
            "expected": item["expected_answer"],
            "actual": actual,
            "correct": is_correct,
        })
        print(f"{'✓' if is_correct else '✗'} {item['question'][:60]}...")

    score = sum(1 for r in results if r["correct"]) / len(results) if results else 0

    print(f"\n=== Résultat évaluation RAG ===")
    print(f"Score : {sum(r['correct'] for r in results)}/{len(results)} ({score:.1%})")

    return {"score": score, "details": results}
