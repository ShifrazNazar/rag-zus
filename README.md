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
OPENAI_API_KEY=your_openai_api_key_here
```

### Frontend

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

## 📚 Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)

## 🚢 Deployment

- **Backend**: Deploy to Railway/Render
- **Frontend**: Deploy to Vercel

See individual README files for deployment instructions.
