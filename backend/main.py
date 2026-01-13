from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from routers import upload, query
from config import RATE_LIMIT

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Mini RAG API",
    description="Retrieval-Augmented Generation with Pinecone + Gemini",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


app.include_router(upload.router)
app.include_router(query.router)


@app.get("/")
async def root():
    return {
        "name": "Mini RAG API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /api/upload",
            "query": "POST /api/query",
            "documents": "GET /api/documents",
            "health": "GET /api/health"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
