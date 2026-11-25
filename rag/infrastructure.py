"""Pinecone 7.x index lifecycle and bounded ingestion."""
import time
from pinecone import ServerlessSpec
from rag.config import DIMENSION

def ensure_index(pc, name, timeout=120):
    if name not in pc.list_indexes().names():
        pc.create_index(name=name, dimension=DIMENSION, metric='cosine',
                        spec=ServerlessSpec(cloud='aws', region='us-east-1'))
    deadline = time.monotonic() + timeout
    while True:
        description = pc.describe_index(name)
        if description.dimension != DIMENSION or description.metric != 'cosine':
            raise ValueError('El índice debe tener dimensión 1536 y métrica cosine.')
        if description.status['ready']:
            return description
        if time.monotonic() >= deadline:
            raise TimeoutError('El índice no estuvo disponible dentro del plazo.')
        time.sleep(2)

def upload(index, embeddings, docs, namespace):
    for offset in range(0, len(docs), 64):
        batch = docs[offset:offset+64]
        vectors = embeddings.embed_documents([doc.page_content for doc in batch])
        if len(vectors) != len(batch) or any(len(v) != DIMENSION for v in vectors):
            raise ValueError('Embeddings incompatibles: se esperan 1536 dimensiones.')
        index.upsert(vectors=[{'id': d.metadata['chunk_id'], 'values': v,
                              'metadata': {**d.metadata, 'text': d.page_content}}
                             for d, v in zip(batch, vectors)], namespace=namespace)
    deadline = time.monotonic() + 120
    pending = {d.metadata['chunk_id'] for d in docs}
    while pending:
        for offset in range(0, len(docs), 500):
            ids = [d.metadata['chunk_id'] for d in docs[offset:offset+500] if d.metadata['chunk_id'] in pending]
            if ids:
                response = index.fetch(ids=ids, namespace=namespace)
                pending.difference_update(response.vectors)
        if pending:
            if time.monotonic() >= deadline:
                raise TimeoutError('La ingesta aún no es visible; repetir ingest.py.')
            time.sleep(2)
