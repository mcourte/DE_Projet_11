import logging
import pandas as pd
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

from src.vectorstore.embeddings import get_embeddings_model

logger = logging.getLogger(__name__)

FAISS_INDEX_PATH = "data/processed/faiss_index"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


def build_documents(df: pd.DataFrame) -> list[Document]:
    documents = []
    for _, row in df.iterrows():
        content = f"Titre : {row['title']}\nDescription : {row['description']}"
        metadata = {
            "id": row["id"],
            "title": row["title"],
            "city": row["city"],
            "address": row["address"],
            "first_date": row["first_date"],
            "url": row["url"],
        }
        documents.append(Document(page_content=content, metadata=metadata))
    logger.info(f"{len(documents)} documents créés")
    return documents


def chunk_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"{len(chunks)} chunks générés")
    return chunks


def build_index(df: pd.DataFrame) -> FAISS:
    embeddings_model = get_embeddings_model()
    documents = build_documents(df)
    chunks = chunk_documents(documents)

    logger.info("Vectorisation en cours (appel API Mistral)...")
    batch_size = 32
    faiss_index = None
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        logger.info(f"Batch {i // batch_size + 1}/{(len(chunks) - 1) // batch_size + 1} ({len(batch)} chunks)...")
        if faiss_index is None:
            faiss_index = FAISS.from_documents(batch, embeddings_model)
        else:
            faiss_index.add_documents(batch)

    Path(FAISS_INDEX_PATH).parent.mkdir(parents=True, exist_ok=True)
    faiss_index.save_local(FAISS_INDEX_PATH)
    logger.info(f"Index FAISS sauvegardé → {FAISS_INDEX_PATH}")
    return faiss_index


def load_index() -> FAISS:
    embeddings_model = get_embeddings_model()
    return FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings_model,
        allow_dangerous_deserialization=True,
    )
