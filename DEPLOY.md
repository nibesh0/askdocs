# Deployment Guide: AskDocs

## Backend: Render

### Step 1: Create Render Account
1. Go to [render.com](https://render.com) and sign up with GitHub

### Step 2: Create New Web Service
1. Click **New → Web Service**
2. Connect your **nibesh0/askdocs** repository
3. Configure:
   - **Name**: `askdocs-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables
In Render dashboard, add these environment variables:
- `GEMINI_API_KEY` = your Gemini API key
- `PINECONE_API_KEY` = your Pinecone API key  
- `PINECONE_HOST` = your Pinecone host URL

### Step 4: Deploy
Click **Create Web Service** - Render will build and deploy automatically.

Your backend URL will be: `https://askdocs-backend.onrender.com`

---

## Frontend: Vercel

### Step 1: Create Vercel Account
1. Go to [vercel.com](https://vercel.com) and sign up with GitHub

### Step 2: Import Project
1. Click **Add New → Project**
2. Import **nibesh0/askdocs** repository
3. Configure:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`

### Step 3: Add Environment Variable
- `NEXT_PUBLIC_API_URL` = `https://askdocs-backend.onrender.com`

### Step 4: Deploy
Click **Deploy** - Vercel will build and deploy automatically.

Your frontend URL will be: `https://askdocs.vercel.app`

---

## Post-Deployment

### Update CORS (if needed)
Add your Vercel domain to backend CORS settings in `backend/main.py`.
