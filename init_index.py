from pinecone import Pinecone
from rag.config import Settings
from rag.infrastructure import ensure_index

def main():
    settings = Settings.load(require_openai=False)
    ensure_index(Pinecone(api_key=settings.pinecone_key), settings.index_name)
    print(f'Índice disponible: {settings.index_name} (1536, cosine, Serverless)')

if __name__ == '__main__':
    main()
