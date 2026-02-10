import re

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from env_utils import OPENAI_API_KEY, OPENAI_BASE_URL


def _normalize_search_item(item: dict) -> tuple[str, str]:
    content = item.get("content") or item.get("snippet") or item.get("title") or ""
    url = item.get("url") or item.get("link") or ""
    return content, url


def build_retriever_FAISS(raw_data_list):
    docs = []
    for idx, item in enumerate(raw_data_list):
        content, url = _normalize_search_item(item)
        if not content:
            continue
        docs.append(
            Document(
                page_content=content,
                metadata={"source_id": f"doc_{idx}", "url": url},
            )
        )

    embeddings = OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )

    vs = FAISS.from_documents(docs, embeddings)
    return vs.as_retriever(search_kwargs={"k": 5})


def build_retriever_chroma(raw_data_list, enhanced_query):
    if not raw_data_list:
        raise ValueError("No data retrieved from search, pls double check.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
    )

    all_docs = []
    for idx, item in enumerate(raw_data_list):
        raw_text, url = _normalize_search_item(item)
        cleaned_raw = re.sub(r"\s+", " ", raw_text).strip()
        if not cleaned_raw:
            continue
        docs = text_splitter.create_documents(
            [cleaned_raw],
            metadatas=[{"source_id": f"doc_{idx}", "url": url}],
        )
        all_docs.extend(docs)

    embed_model = OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    vectorstore = Chroma.from_documents(documents=all_docs, embedding=embed_model)
    return vectorstore.as_retriever(search_kwargs={"k": 5})