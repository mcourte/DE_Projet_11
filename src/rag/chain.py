import os
from langchain_mistralai import ChatMistralAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

PROMPT_TEMPLATE = """Tu es un assistant spécialisé dans la recommandation d'événements culturels pour Puls-Events.
Réponds uniquement à partir des informations du contexte ci-dessous.
Si aucun événement ne correspond à la question, dis-le clairement sans inventer.

Contexte :
{context}

Question : {question}

Réponse :"""


def build_rag_chain(vectorstore: FAISS) -> RetrievalQA:
    llm = ChatMistralAI(
        model="mistral-large-latest",
        mistral_api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0.1,
    )
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )
