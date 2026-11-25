"""Configuration shared by all command line tools."""
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'text-embedding-3-small'
DIMENSION = 1536

@dataclass(frozen=True)
class Settings:
    pinecone_key: str
    openai_key: str
    index_name: str
    namespace: str

    @classmethod
    def load(cls, require_openai=True):
        load_dotenv(ROOT / '.env')
        required = ['PINECONE_API_KEY', 'INDEX_NAME', 'PINECONE_NAMESPACE']
        if require_openai:
            required.append('OPENAI_API_KEY')
        missing = [key for key in required if not os.getenv(key, '').strip()]
        if missing:
            raise ValueError('Configurar en .env: ' + ', '.join(missing))
        return cls(os.environ['PINECONE_API_KEY'], os.getenv('OPENAI_API_KEY', ''),
                   os.environ['INDEX_NAME'], os.environ['PINECONE_NAMESPACE'])
