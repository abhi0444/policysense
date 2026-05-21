"""
Vector store for policy RAG using ChromaDB.
Not used in the main flow yet — keeping it for longer documents.
"""

import os
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter


_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


def _get_embeddings():
    provider = os.getenv("LLM_PROVIDER", "groq")
    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings()
    elif provider == "bedrock":
        from langchain_aws import BedrockEmbeddings
        return BedrockEmbeddings(region_name=os.getenv("AWS_REGION", "us-east-1"))
    return None


def create_policy_store(policy_text: str, policy_id: str) -> Chroma:
    chunks = _splitter.split_text(policy_text)
    metadatas = [{"policy_id": policy_id, "chunk_index": i} for i in range(len(chunks))]
    collection = f"policy_{policy_id.replace('.', '_').replace(' ', '_')[:50]}"

    embeddings = _get_embeddings()
    if embeddings:
        return Chroma.from_texts(texts=chunks, embedding=embeddings, metadatas=metadatas, collection_name=collection)
    return Chroma.from_texts(texts=chunks, metadatas=metadatas, collection_name=collection)


def query_policy(store: Chroma, question: str, k: int = 4) -> list[str]:
    docs = store.similarity_search(question, k=k)
    return [doc.page_content for doc in docs]
