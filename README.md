# Mini RAG 🔍

A full-stack Retrieval-Augmented Generation (RAG) application with cloud vector database, semantic search, reranking, and LLM-powered answers with citations.

![Architecture](https://img.shields.io/badge/Stack-Pinecone%20%2B%20Gemini-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

- **Document Upload** - Upload text files (.txt, .pdf, .md) or paste text directly
- **Smart Chunking** - Token-based semantic chunking with overlap for context preservation
- **Vector Search** - Pinecone-powered similarity search with top-K retrieval
- **Reranking** - Gemini-based relevance reranking for improved accuracy
- **Cited Answers** - LLM responses with inline citations [1], [2] mapped to sources
- **Cost Tracking** - Request timing and token/cost estimates displayed

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────────────────────────────┐
│                 │     │              Backend (FastAPI)          │
│    Frontend     │────▶│                                         │
│   (Next.js)     │     │  ┌─────────┐  ┌──────────┐  ┌────────┐ │
│                 │◀────│  │ Chunker │─▶│ Embedder │─▶│Pinecone│ │
└─────────────────┘     │  └─────────┘  └──────────┘  └────────┘ │
                        │                                         │
                        │  ┌─────────┐  ┌──────────┐  ┌────────┐ │
                        │  │Retriever│─▶│ Reranker │─▶│  LLM   │ │
                        │  └─────────┘  └──────────┘  └────────┘ │
                        └─────────────────────────────────────────┘
```

## 📋 Index Configuration

| Property | Value |
|----------|-------|
| **Index Name** | `mini-rag-index` |
| **Host** | `mini-rag-index-4ngvhcs.svc.aped-4627-b74a.pinecone.io` |
| **Dimensions** | 768 (Gemini text-embedding-004) |
| **Metric** | Cosine similarity |
| **Upsert Batch** | 100 vectors/batch |
| **Namespace Strategy** | Per-document (`doc_{uuid}`) |

## 🔧 Chunking Parameters

| Parameter | Value |
|-----------|-------|
| **Token Model** | tiktoken `cl100k_base` |
| **Chunk Size** | 1000 tokens |
| **Overlap** | 100 tokens (10%) |
| **Splitter** | Semantic (paragraph → sentence → char fallback) |

## 🛠️ Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Pinecone account (free tier works)
- Google AI Studio API key

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

Create `.env` in the project root:
```env
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

Run the backend:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
```

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run the frontend:
```bash
npm run dev
```

Visit `http://localhost:3000`

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload document (file or text) |
| POST | `/api/query` | Query with RAG pipeline |
| GET | `/api/documents` | List indexed documents |
| GET | `/api/health` | Health check |

## 🔄 RAG Pipeline

1. **Embed Query** - Convert query to 768-dim vector (Gemini)
2. **Retrieve** - Get top-10 similar chunks from Pinecone
3. **Rerank** - Score relevance with Gemini, keep top-5
4. **Generate** - Produce answer with citations (Gemini 1.5 Flash)

## 💰 Cost Estimates (per 1000 queries)

| Service | Cost |
|---------|------|
| Embeddings | ~$0.01 |
| LLM (Gemini Flash) | Free tier / ~$0.15 |
| Pinecone | Free tier |
| **Total** | ~$0.16 |

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build individually
docker build -t mini-rag-backend ./backend
docker build -t mini-rag-frontend ./frontend
```

## ☸️ Kubernetes Deployment

```bash
# Create secrets (replace with your actual keys)
kubectl create secret generic mini-rag-secrets \
  --from-literal=gemini-api-key=YOUR_KEY \
  --from-literal=pinecone-api-key=YOUR_KEY

# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=mini-rag
```

**K8s Features:**
- 2 replicas per service with health checks
- HorizontalPodAutoscaler (scales to 10 pods at 70% CPU)
- ConfigMap for environment config
- Secrets for API keys
- Ingress with TLS support

## 📝 Remarks

### Known Limitations
- File size limited to 5MB
- PDF extraction may miss complex layouts
- Reranking adds ~500-1000ms latency (LLM-based)
- No authentication (add for production)

### Trade-offs Made
- **Gemini for reranking** - Using LLM instead of dedicated reranker (Cohere) to minimize API dependencies
- **768-dim embeddings** - Gemini embedding model; OpenAI offers 1536-dim but requires additional API
- **Single namespace query** - Queries target last uploaded document for simplicity

### Future Improvements
- [ ] Add user authentication
- [ ] Implement cross-encoder reranker for faster reranking
- [ ] Add document deletion UI
- [ ] Support more file formats (docx, html)
- [ ] Add conversation memory for follow-up questions
- [ ] Implement MMR for diverse retrieval
- [ ] Add streaming responses

## 🔗 Links

- **Live URL**: [Coming soon]
- **Resume**: [Your resume link here]

## 📄 License

MIT License - feel free to use and modify!
