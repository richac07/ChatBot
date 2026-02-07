# RAG ChatBot (Cloud Ready)

A Retrieval-Augmented Generation (RAG) system for customer support, leveraging **Groq (Llama 3.1)** for fast cloud inference, LangChain for orchestration, and ChromaDB for vector storage. Features a premium Next.js frontend.

---

## 🛠️ Technical Stack

### Frontend (User Interface)
- **Framework**: [Next.js](https://nextjs.org/) (React 18+, App Router)
- **Language**: TypeScript (`.tsx`)
- **Styling**: CSS Modules (`page.module.css`) & Global CSS
- **State Management**: React Hooks (`useState`, `useEffect`, `useRef`)
- **API Client**: Native Fetch API

### Backend (API & Logic)
- **Server Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python Asynchronous Web Framework)
- **Server Runner**: [Uvicorn](https://www.uvicorn.org/) (ASGI server)
- **Orchestration**: [LangChain](https://www.langchain.com/) (Framework for LLM apps)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/) (Local/In-memory vector store)

### AI & Models
- **LLM**: [Groq](https://groq.com/) (Serving Llama 3.1 8B Instant) - *Optimized for speed*
- **Embeddings**: [Hugging Face](https://huggingface.co/) (BAAI/bge-small-en-v1.5) - *Via Inference API*

---

## 🔌 Frontend-Backend Communication (TSX ↔ API)

The React frontend (`page.tsx`) communicates with the Python backend (`api.py`) using standard HTTP requests.

1.  **User Input**: The user types a question in the chat input.
2.  **React State**: The generic `handleSend` function is triggered.
3.  **API Call**: The frontend sends a `POST` request to the backend.

### Code Snippet (`page.tsx`)
```typescript
// The frontend determines the API URL from environment variables
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Sends the user's question as a JSON payload
const response = await fetch(`${apiUrl}/ask`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ question: input }), // { "question": "Return policy?" }
});

const data = await response.json(); // { "answer": "You can return..." }
```

---

## ⚙️ Backend Logic & API Workflow

The backend is built with **FastAPI** in `api.py`. It serves as the bridge between the frontend and the LangChain logic.

### API Endpoint (`api.py`)
- **Route**: `POST /ask`
- **Request Model**: Expects a JSON object matching `QuestionRequest` (`{"question": "str"}`).
- **Response Model**: Returns `AnswerResponse` (`{"answer": "str"}`).

### Workflow Steps
1.  **Request Reception**: FastAPI receives the `POST /ask` request.
2.  **Validation**: Pydantic validates that the request body contains a string `question`.
3.  **Lazy Loading**: The specialized `query` module is imported only when needed (to speed up server start time).
4.  **Processing**: The `query(question)` function is called.
5.  **Response**: The generated answer string is wrapped in a JSON response and sent back to the frontend.

```python
# api.py
@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    # Dynamic import to keep startup fast
    from query import query
    response = query(request.question)
    return AnswerResponse(answer=response)
```

---

## 🔄 Data Flow (The RAG Pipeline)

The core logic resides in `query.py`. This is how the system generates an answer:

### 1. Document Loading & Splitting
- **Source**: `docs/faq.txt` contains the knowledge base.
- **Action**: The text is loaded and split into small chunks (e.g., 30 characters) using `CharacterTextSplitter`. This ensures that we only retrieve relevant snippets, not the whole document.

### 2. Embedding Generation
- **Tool**: Hugging Face Inference API (`BAAI/bge-small-en-v1.5`).
- **Action**: Both the document chunks and the user's question are converted into numerical vectors (embeddings).

### 3. Vector Storage & Retrieval
- **Store**: **ChromaDB** creates an in-memory vector store from the document embeddings.
- **Retrieval**: When a user asks a question, the system searches ChromaDB for the chunks most similar to the question's embedding.

### 4. Generation (LLM)
- **Context Construction**: The retrieved chunks are combined into a prompt.
- **Prompt Template**:
  ```text
  You are a customer support specialist...
  question: {user_question}
  context: {retrieved_chunks}
  ```
- **Inference**: The prompt is sent to **Groq** (hosting Llama 3.1).
- **Output**: The LLM generates a natural language response based *only* on the provided context.

---

## 🏗️ Architecture Diagram

```mermaid
graph TD
    User[User] -- "1. Types Question" --> Frontend[Next.js Frontend]
    Frontend -- "2. POST /ask (JSON)" --> API[FastAPI Backend]
    
    subgraph Backend [Backend Server]
        API -- "3. Validates Request" --> Logic[Query Module]
        Logic -- "4. Loads & Splits Docs" --> Loader[Document Loader]
        Logic -- "5. Embeds Question" --> Embed[Hugging Face Embeddings]
        Logic -- "6. Retrieve Semantically Similar" --> Chroma[ChromaDB]
        Chroma -- "7. Returns Context Chunks" --> Logic
        Logic -- "8. Sends Prompt + Context" --> LLM[Groq (Llama 3.1)]
        LLM -- "9. Generates Answer" --> Logic
    end
    
    Logic -- "10. Returns Answer String" --> API
    API -- "11. JSON Response" --> Frontend
    Frontend -- "12. Displays Message" --> User
```

---

## 🚀 Setup & Usage

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- API Keys for **Groq** and **Hugging Face**.

### 2. Backend Setup
```bash
# Create virtual environment
python3 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python api.py
# Server runs at http://localhost:8000
```

### 3. Frontend Setup
```bash
cd chatbot-ui

# Install dependencies
npm install

# Run development server
npm run dev
# App runs at http://localhost:3000
```

### 4. Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_key
HUGGINGFACEHUB_API_TOKEN=your_hf_token
```
For the frontend (optional if running locally on default ports), create `chatbot-ui/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```
