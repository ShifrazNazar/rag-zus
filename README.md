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
