# Mindhive AI Chatbot - Backend

FastAPI backend for the Mindhive multi-agent chatbot with RAG, Text2SQL, tool calling, and calculator functionality.

## Tech Stack

- **Framework**: FastAPI
- **AI/ML**: LangChain, OpenAI/Anthropic API
- **Vector Store**: FAISS
- **Database**: SQLite (via SQLAlchemy)
- **Validation**: Pydantic
- **Testing**: pytest

## Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── routers/               # API endpoint routers
│   ├── calculator.py      # POST /calculate
│   ├── products.py        # GET /products?query=<text>
│   ├── outlets.py         # GET /outlets?query=<nl>
│   └── chat.py            # POST /chat (main agent endpoint)
├── services/              # Business logic services
│   ├── agent_planner.py   # Intent parsing, action selection
│   ├── memory_manager.py  # Conversation state tracking
│   ├── rag_service.py     # Vector store + retrieval
│   ├── text2sql_service.py # NL to SQL translation
│   └── tool_executor.py   # Tool call wrapper with error handling
├── models/                # Data models
│   ├── schemas.py         # Pydantic request/response models
│   └── database.py        # SQLite connection and models
├── data/                  # Data files
│   ├── outlets.db         # SQLite database
│   ├── products/          # Scraped product data (JSON)
│   └── faiss_index/       # Vector store files
├── scripts/               # Utility scripts
│   ├── scrape_products.py # Scrape shop.zuscoffee.com drinkware
│   └── scrape_outlets.py # Scrape zuscoffee.com outlets
└── tests/                 # Test files
    ├── test_calculator.py
    ├── test_products.py
    ├── test_outlets.py
    └── test_agent.py
```

## Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   ```bash
   # macOS/Linux
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   # OR
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Running the Server

### Development Mode (with auto-reload)

```bash
uvicorn main:app --reload --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Using Python directly

```bash
python main.py
```

The server will start at `http://localhost:8000`

## API Documentation

Once the server is running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

- **GET** `/health`
  - Returns server health status
  - Response: `{"status": "healthy", "service": "mindhive-chatbot"}`

### Calculator

- **POST** `/calculate`
  - Evaluates mathematical expressions safely
  - Request body: `{"expression": "2 + 2"}`
  - Response: `{"result": 4}` or `{"error": "Invalid expression"}`

### Products Search (RAG)

- **GET** `/products?query=<search_term>`
  - Searches products using RAG (Retrieval Augmented Generation)
  - Returns top-3 relevant products with LLM-generated summary
  - Example: `GET /products?query=tumbler`

### Outlets Search (Text2SQL)

- **GET** `/outlets?query=<natural_language_query>`
  - Converts natural language to SQL and queries outlets database
  - Returns matching outlets with location details
  - Example: `GET /outlets?query=outlets in petaling jaya`

### Chat Agent

- **POST** `/chat`
  - Main multi-agent chat endpoint
  - Handles intent classification, tool calling, and conversation memory
  - Request body:
    ```json
    {
      "message": "What products do you have?",
      "history": [
        {"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00Z"},
        {"role": "assistant", "content": "Hi! How can I help?", "timestamp": "2024-01-01T00:00:01Z"}
      ]
    }
    ```
  - Response:
    ```json
    {
      "response": "We have various drinkware products...",
      "tool_calls": [...],
      "intent": "product_search",
      "memory": {...}
    }
    ```

## Data Setup

### Scraping Products

```bash
python scripts/scrape_products.py
```

This scrapes drinkware products from `shop.zuscoffee.com` and saves them as JSON files in `data/products/`.

### Scraping Outlets

```bash
python scripts/scrape_outlets.py
```

This scrapes outlet information from `zuscoffee.com` and populates the SQLite database at `data/outlets.db`.

### Building FAISS Index

The FAISS index for product search is automatically built when the RAG service is first initialized. Product data should be in `data/products/` before starting the server.

## Testing

Run all tests:

```bash
pytest -v
```

Run specific test file:

```bash
pytest tests/test_calculator.py -v
```

Run with coverage:

```bash
pytest --cov=. --cov-report=html
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM and embeddings | Yes (or ANTHROPIC_API_KEY) |
| `ANTHROPIC_API_KEY` | Anthropic API key (alternative to OpenAI) | Yes (or OPENAI_API_KEY) |
| `HOST` | Server host (default: 0.0.0.0) | No |
| `PORT` | Server port (default: 8000) | No |
| `ENVIRONMENT` | Environment mode (development/production) | No |

## Development Guidelines

### Code Style

- Use type hints for all functions: `def calculate(expression: str) -> dict[str, Any]:`
- Async/await for all I/O operations
- Pydantic models for request/response validation
- Google-style docstrings for public functions
- Max line length: 100 characters

### Error Handling

- Always return structured JSON errors, never raise unhandled exceptions
- Use logging module: INFO for actions, ERROR for failures
- Provide user-friendly error messages

### Security

- **NEVER** use `eval()` for calculator - use `ast.literal_eval`
- **ALWAYS** sanitize SQL queries (parameterized queries only)
- **NEVER** expose API keys in code or logs
- **ALWAYS** validate input with Pydantic models
- Rate limiting: 10 req/min per IP (to be implemented)

## Troubleshooting

### Import Errors

If you see import errors, make sure:
1. Virtual environment is activated
2. All dependencies are installed: `pip install -r requirements.txt`

### Database Errors

If SQLite database doesn't exist:
1. Run `python scripts/scrape_outlets.py` to create and populate it
2. Ensure `data/` directory exists and is writable

### FAISS Index Errors

If FAISS index is missing:
1. Ensure product data exists in `data/products/`
2. Restart the server - index will be built on first RAG query

### API Key Errors

If you see API key errors:
1. Check `.env` file exists and contains valid API key
2. Ensure `.env` is in the `backend/` directory
3. Restart the server after adding/changing API keys

## Deployment

### Railway/Render

1. Set environment variables in platform dashboard
2. Ensure `requirements.txt` is in repository
3. Platform will auto-detect FastAPI and run `uvicorn main:app`

### Docker (Optional)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## License

Part of the Mindhive technical assessment project.

