from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import time
import os

from services.chunker import chunk_text
from services.embedder import embed_texts
from services.vector_store import upsert_vectors
from config import MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload")
async def upload_document(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    title: Optional[str] = Form("Untitled Document"),
    namespace: Optional[str] = Form(None)
):
    start_time = time.time()
    
    try:
        if not file and not text:
            raise HTTPException(status_code=400, detail="Provide either a file or text content")
        
        content = ""
        source = "direct_input"
        
        if file:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}"
                )
            
            file_content = await file.read()
            size_mb = len(file_content) / (1024 * 1024)
            if size_mb > MAX_FILE_SIZE_MB:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Max size: {MAX_FILE_SIZE_MB}MB"
                )
            
            if ext == ".pdf":
                try:
                    from pypdf import PdfReader
                    import io
                    reader = PdfReader(io.BytesIO(file_content))
                    content = "\n\n".join([page.extract_text() for page in reader.pages])
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")
            else:
                content = file_content.decode("utf-8")
            
            source = file.filename
            if not title or title == "Untitled Document":
                title = os.path.splitext(file.filename)[0]
        else:
            content = text
        
        if not content or len(content.strip()) < 10:
            raise HTTPException(status_code=400, detail="Content too short")
        
        chunks = chunk_text(content, source=source, title=title)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No chunks generated from content")
        
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = await embed_texts(chunk_texts)
        
        result = await upsert_vectors(embeddings, chunks, namespace=namespace)
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "message": "Document indexed successfully",
            "stats": {
                "chunks_created": len(chunks),
                "namespace": result["namespace"],
                "processing_time_ms": int(processing_time * 1000),
                "avg_chunk_tokens": sum(c["token_count"] for c in chunks) // len(chunks)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/documents")
async def list_documents():
    from services.vector_store import get_index_stats
    stats = await get_index_stats()
    return {
        "total_vectors": stats["total_vectors"],
        "namespaces": stats["namespaces"]
    }
