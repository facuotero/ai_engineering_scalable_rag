"""Hybrid retrieval using weighted reciprocal rank fusion."""
import re
from typing import Any
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from rag.config import MODEL, DIMENSION
from rag.corpus import load_manifest

def tokenize(text):
    return re.findall(r'\w+', text.casefold())

class PineconeRetriever(BaseRetriever):
    index: Any
    embeddings: Any
    namespace: str
    corpus_version: str
    k: int = 20

    def _get_relevant_documents(self, query, *, run_manager):
        result = self.index.query(vector=self.embeddings.embed_query(query), top_k=self.k,
                                  namespace=self.namespace, include_metadata=True,
                                  filter={'corpus_version': {'$eq': self.corpus_version}})
        return [Document(page_content=match['metadata']['text'],
                         metadata={k:v for k,v in match['metadata'].items() if k != 'text'})
                for match in result['matches']]

class RAGSystem:
    def __init__(self, lexical, semantic, max_candidates=20):
        self.max_candidates = min(max_candidates, 10000)
        self.retriever = EnsembleRetriever(retrievers=[lexical, semantic],
                                          weights=[0.5, 0.5], id_key='chunk_id')

    @classmethod
    def from_settings(cls, settings, manifest):
        docs, version = load_manifest(manifest, settings)
        lexical = BM25Retriever.from_documents(docs, preprocess_func=tokenize, k=20)
        pc = Pinecone(api_key=settings.pinecone_key)
        info = pc.describe_index(settings.index_name)
        if info.dimension != DIMENSION or info.metric != 'cosine':
            raise ValueError('El índice debe tener dimensión 1536 y métrica cosine.')
        semantic = PineconeRetriever(index=pc.Index(host=info.host),
            embeddings=OpenAIEmbeddings(model=MODEL, dimensions=DIMENSION, api_key=settings.openai_key),
            namespace=settings.namespace, corpus_version=version)
        return cls(lexical, semantic, max_candidates=len(docs))

    def retrieve(self, query, k=5):
        if not query.strip() or k < 1:
            raise ValueError('La consulta debe contener texto y k debe ser positivo.')
        while True:
            selected, seen = [], set()
            for doc in self.retriever.invoke(query):
                identifier = doc.metadata['document_id']
                if identifier not in seen:
                    selected.append(doc)
                    seen.add(identifier)
                    if len(selected) == k:
                        return selected
            expandable = [r for r in self.retriever.retrievers
                          if hasattr(r, 'k') and r.k < self.max_candidates]
            if not expandable:
                return selected
            for retriever in expandable:
                retriever.k = min(retriever.k * 2, self.max_candidates)
