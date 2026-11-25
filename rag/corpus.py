"""Deterministic Markdown chunking and portable JSON manifests."""
import hashlib
import json
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.config import MODEL

def prepare_corpus(directory):
    directory = Path(directory)
    sources = []
    for path in sorted(directory.rglob('*.md')):
        text = path.read_text(encoding='utf-8').strip()
        if text:
            relative = path.relative_to(directory).as_posix()
            sources.append((relative, text))
    if not sources:
        raise ValueError('El corpus no contiene documentos Markdown con texto.')
    fingerprint = json.dumps([MODEL, 700, 100, sources], ensure_ascii=False)
    version = hashlib.sha256(fingerprint.encode()).hexdigest()
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name='cl100k_base', chunk_size=700, chunk_overlap=100)
    chunks = []
    for relative, text in sources:
        for position, content in enumerate(splitter.split_text(text)):
            identifier = hashlib.sha256(f'{version}:{relative}:{position}'.encode()).hexdigest()
            chunks.append(Document(page_content=content, metadata={
                'document_id': str(Path(relative).with_suffix('')), 'chunk_id': identifier,
                'source': relative, 'categories': [Path(relative).stem.split('_')[0]],
                'corpus_version': version}))
    return chunks, version

def save_manifest(path, docs, version, settings):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {'corpus_version': version, 'index_name': settings.index_name,
               'namespace': settings.namespace, 'model': MODEL,
               'chunks': [{'text': d.page_content, 'metadata': d.metadata} for d in docs]}
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)

def load_manifest(path, settings):
    if not Path(path).exists():
        raise ValueError('Falta el manifiesto local. Ejecutar ingest.py primero.')
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if (data['index_name'], data['namespace'], data['model']) != (settings.index_name, settings.namespace, MODEL):
        raise ValueError('El manifiesto no corresponde al índice, namespace o modelo configurados.')
    docs = [Document(page_content=row['text'], metadata=row['metadata']) for row in data['chunks']]
    if not docs:
        raise ValueError('El manifiesto no contiene chunks.')
    return docs, data['corpus_version']
