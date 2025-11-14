# Backend API

FastAPI backend for the Mindhive chatbot with RAG, Text2SQL, and tool calling.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key_here" > .env
uvicorn main:app --reload --port 8000
```

Get Gemini API key from [Google AI Studio](https://ai.google.dev/).

## API Endpoints

### Health Check

**GET** `/health`

### Calculator

**POST** `/calculate`

```json
{ "expression": "2 + 2" }
```

### Products Search (RAG)

**GET** `/products?query=tumbler`

Returns top-k relevant products from FAISS vector store (20 drinkware items).

### Outlets Search (Text2SQL)

**GET** `/outlets?query=outlets in petaling jaya`

Converts natural language to SQL and queries 209 outlets database.

### Chat Agent

**POST** `/chat`

```json
{
  "message": "Show me tumblers",
  "history": []
}
```

Main multi-agent endpoint with intent classification, tool calling, and memory.

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Services

- **Agent Planner**: Intent classification (LLM + rule-based fallback)
- **Memory Manager**: Conversation state tracking
- **RAG Service**: FAISS vector store (20 drinkware items)
- **Text2SQL Service**: NL to SQL conversion (209 outlets)

## Data Setup

```bash
python scripts/scrape_products.py
python scripts/scrape_outlets.py
```

## Testing

```bash
pytest tests/ -v
pytest --cov=. --cov-report=html
```

**73 tests**: Calculator (23), Products (15), Outlets (14), Agent (21)

## Environment Variables

| Variable         | Description    | Required |
| ---------------- | -------------- | -------- |
| `GEMINI_API_KEY` | Gemini API key | Yes      |

## Deployment

### Railway/Render

Set `GEMINI_API_KEY` environment variable. Health check: `/health`

### Docker

```bash
docker build -t mindhive-backend .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key mindhive-backend
```

## Troubleshooting

- **Import errors**: Activate venv and install dependencies
- **Database errors**: Run `python scripts/scrape_outlets.py`
- **FAISS index**: Restart server or call `POST /products/rebuild-index`
- **API key errors**: Check `.env` file exists with valid key
