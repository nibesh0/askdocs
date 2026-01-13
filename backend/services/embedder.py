import google.generativeai as genai
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GEMINI_API_KEY, EMBEDDING_MODEL

genai.configure(api_key=GEMINI_API_KEY)


async def embed_text(text: str) -> List[float]:
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']


async def embed_texts(texts: List[str], task_type: str = "retrieval_document") -> List[List[float]]:
    embeddings = []
    for text in texts:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type=task_type
        )
        embeddings.append(result['embedding'])
    return embeddings


async def embed_query(query: str) -> List[float]:
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=query,
        task_type="retrieval_query"
    )
    return result['embedding']


def get_embedding_dimension() -> int:
    return 768
