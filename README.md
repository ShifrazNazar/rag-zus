# Mindhive AI Chatbot

Multi-agent chatbot with RAG, Text2SQL, tool calling, and custom React frontend. Built for Mindhive technical assessment.

## 🚀 Quick Start

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add sample data
python scripts/add_sample_outlets.py

# Start server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The frontend will be available at `http://localhost:5173` and will connect to the backend at `http://localhost:8000`.

## 📁 Project Structure

```
mindhive/
├── backend/              # FastAPI backend
│   ├── main.py          # FastAPI app entry
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic
│   ├── models/          # Data models
│   ├── data/            # Data files (DB, products, FAISS)
│   └── tests/           # Test files
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom hooks
│   │   ├── services/    # API service
│   │   └── utils/        # Utilities
│   └── package.json
└── README.md
```

## 🎯 Features

- **Calculator**: Safe mathematical expression evaluation
- **Products RAG**: Semantic search for products using FAISS
- **Outlets Text2SQL**: Natural language to SQL for outlet queries
- **Multi-Agent Chat**: Intelligent intent classification and tool calling
- **Modern UI**: React + TypeScript + shadcn/ui components

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📝 API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Environment Variables

### Backend

Create `backend/.env`:

```env
# Google Gemini API Key (required)
GEMINI_API_KEY=your_gemini_api_key_here
```

**Note**: Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

### Frontend

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

## 📚 Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [Architecture Overview](docs/ARCHITECTURE.md) - System architecture and key trade-offs
- [Agentic Planning](docs/AGENTIC_PLANNING.md) - Decision points and planning logic
- [Example Transcripts](docs/EXAMPLE_TRANSCRIPTS.md) - Example conversations and test scenarios
- [Error Handling Strategy](docs/ERROR_HANDLING_STRATEGY.md) - Security and error handling approach

## 🏗️ Architecture Overview

The system follows a multi-agent architecture with the following key components:

- **Agent Planner**: Intent classification and action selection using LLM (Google Gemini)
- **Memory Manager**: Conversation state tracking across multiple turns
- **RAG Service**: FAISS-based semantic search for products
- **Text2SQL Service**: Natural language to SQL conversion for outlet queries
- **Tool Executor**: Wrapper for tool calls with error handling, timeouts, and circuit breakers

**Key Trade-offs**:

- **FAISS over Pinecone**: Local-first, no API costs, sufficient for <10k docs
- **SQLite over PostgreSQL**: Simpler setup, read-heavy workload, easy to bundle
- **In-Memory State**: Fast access, but not suitable for multi-instance deployment
- **Sequential Tool Execution**: Simpler error handling, predictable behavior

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## 📋 Requirements Coverage

All assessment requirements have been completed:

- ✅ **Part 1**: Sequential Conversation (multi-turn tracking)
- ✅ **Part 2**: Agentic Planning (intent parsing, action selection)
- ✅ **Part 3**: Tool Calling (calculator with error handling)
- ✅ **Part 4**: Custom API & RAG Integration (products, outlets)
- ✅ **Part 5**: Unhappy Flows (missing params, downtime, malicious input)
- ✅ **Part 6**: Frontend Chat UI (React, no Streamlit/Gradio)

See [REQUIREMENTS_CHECKLIST.md](docs/REQUIREMENTS_CHECKLIST.md) for detailed verification.

## 🚢 Deployment

- **Backend**: Deploy to Railway/Render
- **Frontend**: Deploy to Vercel

### Docker Deployment

```bash
# Using Docker Compose
docker-compose up

# Or build individually
cd backend && docker build -t mindhive-backend .
cd frontend && docker build -t mindhive-frontend .
```

See individual README files for deployment instructions.
