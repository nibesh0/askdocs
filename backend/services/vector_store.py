from pinecone import Pinecone
from typing import List, Dict, Optional
import uuid
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PINECONE_API_KEY, PINECONE_HOST

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(host=PINECONE_HOST)


async def upsert_vectors(embeddings: List[List[float]], chunks: List[Dict], namespace: Optional[str] = None, batch_size: int = 100) -> Dict:
    if namespace is None:
        namespace = f"doc_{uuid.uuid4().hex[:8]}"
    
    vectors = []
    for i, (embedding, chunk) in enumerate(zip(embeddings, chunks)):
        # Use unique ID per chunk to prevent overwrites when adding multiple files
        chunk_id = f"{namespace}_{uuid.uuid4().hex[:8]}_{i}"
        vectors.append({
            "id": chunk_id,
            "values": embedding,
            "metadata": {
                "text": chunk["text"],
                "source": chunk.get("source", "unknown"),
                "title": chunk.get("title", "Untitled"),
                "chunk_index": chunk.get("chunk_index", i)
            }
        })
    
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch, namespace=namespace)
    
    return {"namespace": namespace, "vectors_upserted": len(vectors)}


async def query_vectors(query_embedding: List[float], namespace: str = None, top_k: int = 10) -> List[Dict]:
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace
    )
    
    documents = []
    for match in results.matches:
        documents.append({
            "id": match.id,
            "score": match.score,
            "text": match.metadata.get("text", ""),
            "source": match.metadata.get("source", "unknown"),
            "title": match.metadata.get("title", "Untitled")
        })
    
    return documents


async def get_index_stats() -> Dict:
    stats = index.describe_index_stats()
    return {
        "total_vectors": stats.total_vector_count,
        "namespaces": list(stats.namespaces.keys()) if stats.namespaces else []
    }


async def delete_namespace(namespace: str):
    index.delete(delete_all=True, namespace=namespace)
