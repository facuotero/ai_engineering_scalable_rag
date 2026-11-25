import argparse
from rag.config import ROOT, Settings
from rag.system import RAGSystem

def main():
    parser = argparse.ArgumentParser(description='Recuperación híbrida BM25 + Pinecone')
    parser.add_argument('query')
    parser.add_argument('--manifest', default=str(ROOT/'artifacts/corpus.json'))
    args = parser.parse_args()
    for rank, doc in enumerate(RAGSystem.from_settings(Settings.load(), args.manifest).retrieve(args.query), 1):
        print(f"\n{rank}. {doc.metadata['source']} [{doc.metadata['document_id']}]\n{doc.page_content}")

if __name__ == '__main__':
    main()
