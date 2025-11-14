# Mindhive AI Chatbot

Multi-agent chatbot with RAG, Text2SQL, tool calling, and custom React frontend. Built for Mindhive technical assessment.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ (for backend)
- Node.js 18+ and npm (for frontend)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here

# Scrape data (optional - sample data included)
python scripts/scrape_products.py
python scripts/scrape_outlets.py

# Start server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables (optional)
# Create .env file with: VITE_API_URL=http://localhost:8000

# Start dev server
npm run dev
```

The frontend will be available at `http://localhost:5173` and will connect to the backend at `http://localhost:8000`.

## 📁 Project Structure

```
mindhive/
├── backend/              # FastAPI backend
│   ├── main.py          # FastAPI app entry with CORS, global exception handler
│   ├── routers/         # API endpoints
│   │   ├── calculator.py      # POST /calculate
│   │   ├── products.py        # GET /products?query=<text>
│   │   ├── outlets.py         # GET /outlets?query=<nl>
│   │   └── chat.py           # POST /chat (main agent endpoint)
│   ├── services/        # Business logic
│   │   ├── agent_planner.py   # Intent parsing, action selection (LLM + rule-based)
│   │   ├── memory_manager.py  # Conversation state tracking
│   │   ├── rag_service.py     # Vector store + retrieval (FAISS, drinkware only)
│   │   ├── text2sql_service.py # NL to SQL translation (SQL injection protection)
│   │   └── tool_executor.py   # Tool call wrapper with error handling
│   ├── models/          # Data models
│   │   ├── schemas.py         # Pydantic request/response models
│   │   └── database.py        # SQLite connection and models
│   ├── data/            # Data files
│   │   ├── outlets.db         # SQLite database (209 outlets)
│   │   ├── products/          # Scraped product data (JSON, 17 drinkware items)
│   │   └── faiss_index/       # Vector store files
│   ├── scripts/         # Utility scripts
│   │   ├── scrape_products.py # Scrape shop.zuscoffee.com drinkware
│   │   └── scrape_outlets.py  # Scrape zuscoffee.com outlets
│   └── tests/           # Test files
│       ├── test_calculator.py
│       ├── test_products.py
│       ├── test_outlets.py
│       └── test_agent.py
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   │   ├── ChatWindow.tsx      # Main chat container
│   │   │   ├── MessageList.tsx     # Message display
│   │   │   ├── MessageBubble.tsx   # Individual message
│   │   │   ├── InputComposer.tsx   # Message input
│   │   │   ├── QuickActions.tsx    # Quick action buttons
│   │   │   ├── ToolCallCard.tsx    # Tool call visualization
│   │   │   ├── BackendStatus.tsx   # Health check indicator
│   │   │   ├── ErrorBoundary.tsx   # Error handling
│   │   │   └── ui/                 # shadcn/ui components
│   │   ├── hooks/       # Custom hooks
│   │   │   └── useChat.ts          # Chat state management
│   │   ├── services/    # API service
│   │   │   └── api.ts              # Backend API calls
│   │   └── utils/        # Utilities
│   │       └── localStorage.ts     # Conversation persistence
│   └── package.json
└── README.md
```

## 🎯 Features

### Core Capabilities

- **Calculator**: Safe mathematical expression evaluation using `ast.literal_eval` (no `eval()`)
- **Products RAG**: Semantic search for drinkware products using FAISS vector store
  - Filters to only "Tumbler" and "Mugs" categories (17 items)
  - Returns top-k results with similarity scores
- **Outlets Text2SQL**: Natural language to SQL conversion for outlet queries
  - Supports 209 outlets from Kuala Lumpur/Selangor
  - SQL injection protection with whitelist/blacklist
  - Handles location-based queries (Petaling Jaya, KL, etc.)
- **Multi-Agent Chat**: Intelligent intent classification and tool calling
  - LLM-based intent classification (Google Gemini) with rule-based fallback
  - Multi-turn conversation tracking
  - Follow-up question handling (e.g., "SS 2, what's the opening time?")

### Example Conversation Flow

1. **User**: "Is there an outlet in Petaling Jaya?"

   - **Bot**: Lists outlets, asks "Which outlet are you referring to?"

2. **User**: "SS 2, what's the opening time?"

   - **Bot**: "Ah yes, the ZUS Coffee – SS2 opens at 9:00 AM - 10:00 PM."

3. **User**: "Show me tumblers"
   - **Bot**: Lists relevant tumbler products with prices

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v

# With coverage
pytest --cov=. --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test

# With UI
npm run test:ui

# With coverage
npm run test:coverage
```

## 📝 API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `GET /health` - Health check
- `POST /calculate` - Calculator tool
- `GET /products?query=<text>` - Product search (RAG)
- `GET /outlets?query=<nl>` - Outlet search (Text2SQL)
- `POST /chat` - Main chat agent endpoint

See [Backend README](backend/README.md) for detailed API documentation.

## 🔧 Environment Variables

### Backend

Create `backend/.env`:

```env
# Google Gemini API Key (required for LLM features)
GEMINI_API_KEY=your_gemini_api_key_here
```

**Note**: Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

### Frontend

Create `frontend/.env` (optional):

```env
VITE_API_URL=http://localhost:8000
```

Defaults to `http://localhost:8000` if not set.

## 🏗️ Architecture Overview

The system follows a multi-agent architecture with the following key components:

### Backend Services

- **Agent Planner**: Intent classification using LLM (Google Gemini) with rule-based fallback

  - Detects: calculator, product_search, outlet_query, general_chat, reset
  - Extracts slots (expression, query, followup)
  - Selects actions (ask_clarification, call_calculator, call_products, call_outlets)

- **Memory Manager**: Conversation state tracking

  - Tracks slots, context, and conversation history
  - Stores last outlets for follow-up queries
  - Limits history to 50 messages

- **RAG Service**: FAISS-based semantic search

  - Filters products to drinkware only (Tumbler, Mugs)
  - Uses sentence-transformers for embeddings
  - Chunks product descriptions (500 chars)

- **Text2SQL Service**: Natural language to SQL conversion

  - Uses LangChain SQLDatabaseChain with Google Gemini
  - SQL injection protection (whitelist/blacklist)
  - Fallback SQL generation with quote escaping
  - Handles 209 outlets from Kuala Lumpur/Selangor

- **Tool Executor**: Wrapper for tool calls
  - Handles async/sync functions
  - Structured error responses
  - Logging

### Frontend Components

- **ChatWindow**: Main container with ErrorBoundary
- **MessageList**: Auto-scrolling message display
- **InputComposer**: Multiline input with Enter/Shift+Enter
- **QuickActions**: `/calc`, `/products`, `/outlets`, `/reset` commands
- **ToolCallCard**: Expandable tool call visualization
- **BackendStatus**: Health check indicator (30s polling)

### Key Trade-offs

- **FAISS over Pinecone**: Local-first, no API costs, sufficient for <10k docs
- **SQLite over PostgreSQL**: Simpler setup, read-heavy workload, easy to bundle
- **In-Memory State**: Fast access, but not suitable for multi-instance deployment
- **LLM + Rule-based Fallback**: Better accuracy when LLM available, graceful degradation
- **Drinkware Filtering**: Only indexes Tumbler/Mugs categories (assignment requirement)

## 📋 Requirements Coverage

All assessment requirements have been completed:

- ✅ **Part 1**: Sequential Conversation (multi-turn tracking with memory)
- ✅ **Part 2**: Agentic Planning (intent parsing, action selection, LLM + fallback)
- ✅ **Part 3**: Tool Calling (calculator with error handling)
- ✅ **Part 4**: Custom API & RAG Integration
  - ✅ Products RAG endpoint (drinkware only, FAISS vector store)
  - ✅ Outlets Text2SQL endpoint (209 outlets, SQL injection protection)
- ✅ **Part 5**: Unhappy Flows (missing params, downtime, malicious input)
- ✅ **Part 6**: Frontend Chat UI (React + TypeScript, no Streamlit/Gradio)

## 🔒 Security Features

- **Calculator**: Uses `ast.literal_eval` instead of `eval()` (safe expression parsing)
- **SQL Injection Protection**: Whitelist/blacklist keywords, quote escaping
- **Input Validation**: Pydantic models for all API requests
- **Error Handling**: Structured error responses, no stack traces exposed

## 🚢 Deployment

### Docker Deployment

```bash
# Using Docker Compose
docker-compose up

# Or build individually
cd backend && docker build -t mindhive-backend .
cd frontend && docker build -t mindhive-frontend .
```

### Platform Deployment

- **Backend**: Deploy to Railway/Render

  - Set `GEMINI_API_KEY` environment variable
  - Health check endpoint: `/health`

- **Frontend**: Deploy to Vercel
  - Set `VITE_API_URL` environment variable
  - Build command: `npm run build`

See individual README files for detailed deployment instructions.

## 📚 Documentation

- [Backend README](backend/README.md) - Backend API documentation and setup
- [Frontend README](frontend/README.md) - Frontend component documentation and setup

## 🐛 Troubleshooting

### Backend Issues

- **Import Errors**: Ensure virtual environment is activated and dependencies installed
- **FAISS Index Missing**: Restart server - index builds automatically on first query
- **API Key Errors**: Check `.env` file exists and contains valid `GEMINI_API_KEY`

### Frontend Issues

- **API Connection**: Check `VITE_API_URL` matches backend URL
- **Build Errors**: Run `npm install` to ensure all dependencies are installed

## 📄 License

Part of the Mindhive technical assessment project.
