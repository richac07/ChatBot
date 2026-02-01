# Red30 Shoes - RAG ChatBot (Cloud Ready)

A Retrieval-Augmented Generation (RAG) system for customer support, leveraging **Groq (Llama 3.1)** for fast cloud inference, LangChain for orchestration, and ChromaDB for vector storage. Features a premium Next.js frontend.

---

## � GitHub Repository Checklist

To run this product seamlessly, ensure your GitHub repository contains these files/folders in this exact structure:

```text
/ (Root)
├── api.py                   # FastAPI Server logic
├── query.py                 # RAG & LangChain logic
├── requirements.txt         # Python dependencies
├── .gitignore               # Ensures sensitive data isn't uploaded
├── docs/
│   └── faq.txt              # Your source documentation
└── chatbot-ui/              # Entire Next.js project folder
```

> [!NOTE]
> Do NOT upload your `env/` folder or your `.env` file containing your API keys.

---

## 🚀 Cloud Deployment (Step-by-Step)

### 1. Backend: [Render.com](https://render.com/)
1. Create a **New > Web Service**.
2. Connect your GitHub repository.
3. **Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api.py`
4. **Environment Variables**:
   - Add `GROQ_API_KEY`: *(Your key from console.groq.com)*
   - Add `ANONYMIZED_TELEMETRY`: `False`
5. Click **Deploy**. Note your service URL (e.g., `https://red30-api.onrender.com`).

### 2. Frontend: [Vercel](https://vercel.com/)
1. Create a **New Project**.
2. Connect the same GitHub repository.
3. **Root Directory Settings**: 
   - Set "Root Directory" to `chatbot-ui`.
4. **Environment Variables**:
   - Add `NEXT_PUBLIC_API_URL`: *(Your Render URL from Step 1)*
5. Click **Deploy**.

---

## 💻 Local Development

### 1. Setup
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=gsk_...
ANONYMIZED_TELEMETRY=False
```

### 3. Run
- **Backend**: `python3 api.py`
- **Frontend**: `cd chatbot-ui && npm run dev`

---

## 🛠️ Tech Stack
- **Frontend**: Next.js 15, Vanilla CSS (Glassmorphism).
- **Backend**: FastAPI, Uvicorn, LangChain.
- **AI**: Groq (Llama 3.1 8B), HuggingFace (Embeddings).
