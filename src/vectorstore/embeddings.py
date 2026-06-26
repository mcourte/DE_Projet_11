import os
from langchain_mistralai import MistralAIEmbeddings
from dotenv import load_dotenv

load_dotenv()


def get_embeddings_model() -> MistralAIEmbeddings:
    return MistralAIEmbeddings(
        model="mistral-embed",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
    )
