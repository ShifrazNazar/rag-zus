# Mindhive Technical Assessment - AI Chatbot

Multi-agent chatbot with RAG, Text2SQL, tool calling, and custom React frontend. Built for Mindhive's AI Software Engineer technical assessment.

## ✨ Quick Summary

- ✅ **All 6 assessment parts** completed
- ✅ **Google Gemini 2.5 Flash** for intent classification and Text2SQL
- ✅ **20 drinkware products** in FAISS vector store
- ✅ **209 outlets** in SQLite database

## 🚀 Quick Start

### Docker (Recommended)

```bash
docker-compose up
```

Backend: `http://localhost:8000` | Frontend: `http://localhost:5173`

**Note**: Set `GEMINI_API_KEY` in `docker-compose.yml` or `.env` file.

### Manual Setup

See [Backend README](backend/README.md) and [Frontend README](frontend/README.md) for detailed setup instructions.

## 📚 Documentation

- **[Backend README](backend/README.md)** - API documentation, setup, and architecture
- **[Frontend README](frontend/README.md)** - Component documentation and setup

## 📋 Assessment Requirements

All 6 parts completed:

- ✅ **Part 1**: Sequential Conversation (multi-turn tracking)
- ✅ **Part 2**: Agentic Planning (intent parsing, action selection)
- ✅ **Part 3**: Tool Calling (calculator with error handling)
- ✅ **Part 4**: Custom API & RAG Integration (Products RAG + Outlets Text2SQL)
- ✅ **Part 5**: Unhappy Flows (missing params, malicious input)
- ✅ **Part 6**: Frontend Chat UI (React + TypeScript)

## 🏗️ Architecture

- **Backend**: FastAPI with LangChain, FAISS, SQLite
- **Frontend**: React + TypeScript with TailwindCSS
- **AI**: Google Gemini 2.5 Flash for intent classification and Text2SQL
- **Memory**: Conversation state tracking with slots and context
- **Security**: SQL injection protection, safe calculator evaluation

## 📄 License

Part of the Mindhive technical assessment project.
