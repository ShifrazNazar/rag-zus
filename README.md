# Mindhive Technical Assessment - AI Chatbot

Multi-agent chatbot with RAG, Text2SQL, tool calling, and custom React frontend. Built for Mindhive's AI Software Engineer technical assessment.

## ✨ Quick Summary

- ✅ **All 6 assessment parts** completed
- ✅ **Google Gemini 2.5 Flash** for intent classification and Text2SQL
- ✅ **20 drinkware products** in FAISS vector store
- ✅ **209 outlets** in SQLite database

## Live
- FE: https://rag-zus.vercel.app
- BE: https://rag-zus.onrender.com/docs

## 🚀 Quick Start

### Docker (Recommended)

```bash
docker-compose up
```

Backend: `http://localhost:8000` | Frontend: `http://localhost:5173`

**Note**: Set `GEMINI_API_KEY` in `docker-compose.yml` or `.env` file.

## 📚 Documentation

- **[Backend README](backend/README.md)** - API documentation, setup, and architecture
- **[Frontend README](frontend/README.md)** - Component documentation and setup

## 📋 Assessment Requirements

All 6 parts completed:

- ✅ **Part 1**: Sequential Conversation (multi-turn tracking)
- ✅ **Part 2**: Agentic Planning (intent parsing, action selection) - [Decision Points](#part-2-decision-points)
- ✅ **Part 3**: Tool Calling (calculator with error handling)
- ✅ **Part 4**: Custom API & RAG Integration (Products RAG + Outlets Text2SQL)
- ✅ **Part 5**: Unhappy Flows (missing params, malicious input) - [Error Handling Strategy](#part-5-error-handling--security)
- ✅ **Part 6**: Frontend Chat UI (React + TypeScript)

### Part 2: Decision Points

The agent planner makes decisions at three key points:

**1. Intent Classification**

- **Decision**: LLM-based (primary) vs Rule-based (fallback)
- **Logic**: Try LLM first for context understanding, fallback to keyword matching if LLM unavailable
- **Output**: Intent type + confidence score + extracted slots

**2. Action Selection**

- **Decision**: `ask_clarification` vs `call_tool` vs `general_chat`
- **Logic**:
  - If missing required slots → `ask_clarification`
  - If slots complete → `call_tool` (calculator/products/outlets)
  - If no clear intent → `general_chat`
- **Example**: "Calculate" → missing `expression` → ask "What would you like to calculate?"

**3. Tool Execution**

- **Decision**: Which tool to call based on intent
- **Logic**: Direct mapping (calculator → `/calculate`, products → `/products`, outlets → `/outlets`)
- **Special Cases**: Outlet follow-ups (hours/services/location) use context from previous query

**Memory Integration**

- **Decision**: When to use stored context vs new query
- **Logic**: For outlet follow-ups, check `last_outlets` in memory before making new API call
- **Example**: "SS 2, what's the opening time?" uses previously fetched outlet data if available

### Part 5: Error Handling & Security

**1. Missing Parameters**

- **Strategy**: Intent analysis detects missing slots → ask clarification
- **Implementation**: `missing_slots` array in intent response triggers `ask_clarification` action
- **Example**: "Calculate" → "What would you like to calculate?"

**2. API Downtime**

- **Strategy**: Try-catch blocks + graceful error messages
- **Implementation**: All tool calls wrapped in try-except, return user-friendly errors
- **Example**: Calculator API fails → "Sorry, I couldn't process that calculation. Please try again."

**3. Malicious Inputs**

- **SQL Injection**: Parameterized queries + SQLAlchemy ORM (no raw SQL)
- **Code Injection**: AST-based safe evaluation for calculator (no `eval()`)
- **XSS**: Input sanitization + React's built-in escaping
- **Test Coverage**: 10+ SQL injection variants, code injection attempts, all handled gracefully

**4. Never Crash**

- **Global Exception Handler**: Catches all unhandled exceptions → returns 500 with generic message
- **Logging**: All errors logged for debugging, but user sees friendly messages
- **Validation**: Pydantic models validate all inputs before processing

## 🏗️ Architecture

- **Backend**: FastAPI with LangChain, FAISS, SQLite
- **Frontend**: React + TypeScript with TailwindCSS
- **AI**: Google Gemini 2.5 Flash for intent classification and Text2SQL
- **Memory**: Conversation state tracking with slots and context
- **Security**: SQL injection protection, safe calculator evaluation

### Architecture Trade-offs

**1. LLM + Rule-based Intent Classification**

- **Choice**: Hybrid approach (LLM primary, rule-based fallback)
- **Trade-off**: LLM provides better accuracy and context understanding, but rule-based ensures reliability when API fails
- **Rationale**: Graceful degradation is critical for production systems

**2. In-Memory Memory Manager**

- **Choice**: Session-based in-memory state (not persisted to DB)
- **Trade-off**: Fast and simple, but state lost on server restart
- **Rationale**: Suitable for assessment; production would use Redis/DB persistence

**3. FAISS for Vector Search**

- **Choice**: FAISS CPU (not GPU) with local file storage
- **Trade-off**: No external dependencies, but slower than GPU/cloud solutions
- **Rationale**: Self-contained, works on any platform, sufficient for 20 products

**4. Text2SQL vs Direct API**

- **Choice**: Text2SQL for outlets (dynamic queries) vs RAG for products (semantic search)
- **Trade-off**: Text2SQL more flexible for structured data, RAG better for unstructured product descriptions
- **Rationale**: Matches data structure - outlets are relational, products are descriptive

**5. Lazy Model Loading**

- **Choice**: Defer SentenceTransformer model loading until first use
- **Trade-off**: First request slower (30-60s), but reduces memory during build/deployment
- **Rationale**: Critical for deployment platforms with memory limits (Vercel, Render)

**6. React Frontend (No Streamlit)**

- **Choice**: Custom React UI instead of Streamlit/Gradio
- **Trade-off**: More development time, but full control and better UX
- **Rationale**: Assessment requirement + production-ready interface

## Flow Diagram

<img width="2668" height="2552" alt="image" src="https://github.com/user-attachments/assets/f3a8bc75-fef1-48c5-9134-bbf5909f33ad" />

## Outlet

<img width="1280" height="832" alt="Screenshot 2025-11-14 at 9 53 13 PM" src="https://github.com/user-attachments/assets/5e7bba9a-de43-43cd-b4ec-a64e6f7da156" />

<img width="1280" height="832" alt="Screenshot 2025-11-14 at 9 55 05 PM" src="https://github.com/user-attachments/assets/8c433736-4b88-4ebd-ad65-3d9d5c2d45c2" />

<img width="1280" height="832" alt="Screenshot 2025-11-14 at 9 56 19 PM" src="https://github.com/user-attachments/assets/ae5258cb-8ffb-4517-8629-2be185f3ff29" />

## Product

<img width="617" height="803" alt="Screenshot 2025-11-14 at 10 10 25 PM" src="https://github.com/user-attachments/assets/18c65a32-2fc6-4f17-a56e-53503934cd6a" />

## Cal

<img width="1280" height="832" alt="Screenshot 2025-11-14 at 10 19 11 PM" src="https://github.com/user-attachments/assets/24e8cb2f-1734-4b0e-bc3f-a078ee2ea11e" />

## 📄 License

Part of the Mindhive technical assessment project.
