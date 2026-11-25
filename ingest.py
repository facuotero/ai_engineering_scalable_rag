import argparse
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from rag.config import ROOT, MODEL, DIMENSION, Settings
from rag.corpus import prepare_corpus, save_manifest
from rag.infrastructure import ensure_index, upload

def main():
    parser = argparse.ArgumentParser(description='Ingesta Markdown → Pinecone + manifiesto BM25')
    parser.add_argument('--documents', type=str, default=str(ROOT/'data/documents'))
    parser.add_argument('--manifest', type=str, default=str(ROOT/'artifacts/corpus.json'))
    args = parser.parse_args()
    settings = Settings.load()
    docs, version = prepare_corpus(args.documents)
    pc = Pinecone(api_key=settings.pinecone_key)
    info = ensure_index(pc, settings.index_name)
    embeddings = OpenAIEmbeddings(model=MODEL, dimensions=DIMENSION, api_key=settings.openai_key)
    upload(pc.Index(host=info.host), embeddings, docs, settings.namespace)
    save_manifest(args.manifest, docs, version, settings)
    print(f'Ingesta completa: {len(docs)} chunks; namespace={settings.namespace}; corpus={version}')

if __name__ == '__main__':
    main()
