from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import time

from services.embedder import embed_query
from services.vector_store import query_vectors
from services.reranker import rerank_documents
from services.llm import generate_answer, estimate_cost
from config import TOP_K_RETRIEVE

router = APIRouter(prefix="/api", tags=["query"])


class QueryRequest(BaseModel):
    query: str
    namespace: Optional[str] = None


@router.post("/query")
async def query_documents(request: QueryRequest):
    start_time = time.time()
    
    try:
        query_embedding = await embed_query(request.query)
        
        retrieved_docs = await query_vectors(
            query_embedding,
            namespace=request.namespace,
            top_k=TOP_K_RETRIEVE
        )
        
        print(f"[DEBUG] Namespace: {request.namespace}")
        print(f"[DEBUG] Retrieved {len(retrieved_docs)} docs")
        sources = set(d.get('source', 'unknown') for d in retrieved_docs)
        print(f"[DEBUG] Sources in retrieved: {sources}")
        
        if not retrieved_docs:
            return {
                "answer": "No documents found. Please upload a document first.",
                "citations": [],
                "timing_ms": int((time.time() - start_time) * 1000),
                "token_estimate": 0
            }
        
        reranked_docs = await rerank_documents(request.query, retrieved_docs)
        
        print(f"[DEBUG] Reranked {len(reranked_docs)} docs")
        sources = set(d.get('source', 'unknown') for d in reranked_docs)
        print(f"[DEBUG] Sources in reranked: {sources}")
        
        if not reranked_docs:
            reranked_docs = retrieved_docs[:5]
        
        result = await generate_answer(request.query, reranked_docs)
        
        cost = estimate_cost(result["token_estimate"])
        
        return {
            "answer": result["answer"],
            "citations": result["citations"],
            "timing_ms": int((time.time() - start_time) * 1000),
            "token_estimate": result["token_estimate"],
            "cost_estimate": cost
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
