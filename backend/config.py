import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

PINECONE_INDEX = os.getenv("PINECONE_INDEX", "mini-rag-index")
PINECONE_HOST = os.getenv("PINECONE_HOST")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

TOP_K_RETRIEVE = 10
TOP_K_RERANK = 5
RERANK_THRESHOLD = 0.1

MAX_FILE_SIZE_MB = 5
ALLOWED_EXTENSIONS = [".txt", ".pdf", ".md"]

RATE_LIMIT = "1000/minute"
