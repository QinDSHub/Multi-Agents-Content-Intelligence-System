import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class SimpleRAG:
    def __init__(self, data_dir: str = "data", embedding_model: str = "text-embedding-3-small"):
        self.data_dir = data_dir
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.vector_store = None
        
    def load_and_index(self) -> bool:
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            return False
        
        documents = []
        for file in os.listdir(self.data_dir):
            if file.endswith('.txt'):
                try:
                    loader = TextLoader(os.path.join(self.data_dir, file), encoding='utf-8')
                    documents.extend(loader.load())
                except:
                    continue
        
        if not documents:
            return False
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_documents(documents)
        
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        return True
    
    def retrieve(self, query: str, k: int = 5) -> str:
        if self.vector_store is None:
            return ""
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return "\n\n".join([doc.page_content for doc in results])
        except:
            return ""
