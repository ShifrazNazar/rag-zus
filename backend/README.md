# Mindhive AI Chatbot - Backend

FastAPI backend for the Mindhive multi-agent chatbot with RAG, Text2SQL, tool calling, and calculator functionality.

## Tech Stack

- **Framework**: FastAPI
- **AI/ML**: LangChain, Google Gemini API (gemini-2.5-flash)
- **Vector Store**: FAISS (with sentence-transformers)
- **Database**: SQLite (via SQLAlchemy)
- **Validation**: Pydantic
- **Testing**: pytest

## Project Structure

```
backend/
├── main.py                 # FastAPI app entry point with CORS, global exception handler
├── requirements.txt        # Python dependencies
├── Dockerfile             # Backend containerization
├── routers/               # API endpoint routers
│   ├── calculator.py      # POST /calculate (safe math evaluation)
│   ├── products.py         # GET /products?query=<text> (RAG search)
│   ├── outlets.py         # GET /outlets?query=<nl> (Text2SQL)
│   └── chat.py            # POST /chat (main agent endpoint)
├── services/              # Business logic services
│   ├── agent_planner.py   # Intent parsing, action selection (LLM + rule-based)
│   ├── memory_manager.py  # Conversation state tracking
│   ├── rag_service.py     # Vector store + retrieval (FAISS, drinkware filtering)
│   ├── text2sql_service.py # NL to SQL translation (SQL injection protection)
│   └── tool_executor.py   # Tool call wrapper with error handling
├── models/                # Data models
│   ├── schemas.py         # Pydantic request/response models
│   └── database.py        # SQLite connection and models
├── data/                  # Data files
│   ├── outlets.db         # SQLite database (209 outlets)
│   ├── products/          # Scraped product data (JSON, 17 drinkware items)
│   │   └── products.json  # Product data (filtered to Tumbler/Mugs)
│   └── faiss_index/       # Vector store files
│       ├── index.faiss    # FAISS index file
│       └── metadata.json  # Product metadata
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

   Edit `.env` and add your API key:

   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

   Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

## Running the Server

### Development Mode (with auto-reload)

```bash
uvicorn main:app --reload --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
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

### Root

- **GET** `/`
  - Returns API information
  - Response: `{"message": "Mindhive AI Chatbot API", "status": "running"}`

### Calculator

- **POST** `/calculate`
  - Evaluates mathematical expressions safely using `ast.literal_eval`
  - **Security**: Never uses `eval()` - only safe AST parsing
  - Request body: `{"expression": "2 + 2"}`
  - Response: `{"result": 4}` or `{"error": "Invalid expression"}`
  - Handles: addition, subtraction, multiplication, division, exponentiation, modulo

### Products Search (RAG)

- **GET** `/products?query=<search_term>&top_k=<number>`

  - Searches products using RAG (Retrieval Augmented Generation)
  - **Filtering**: Only returns drinkware (Tumbler, Mugs categories)
  - Uses FAISS vector store with sentence-transformers embeddings
  - Returns top-k relevant products with similarity scores
  - Example: `GET /products?query=tumbler`
  - Example: `GET /products?query=all products` (returns all drinkware)

- **POST** `/products/rebuild-index`
  - Rebuilds the FAISS index from product data
  - Useful after updating product data

### Outlets Search (Text2SQL)

- **GET** `/outlets?query=<natural_language_query>`
  - Converts natural language to SQL and queries outlets database
  - **Security**: SQL injection protection with whitelist/blacklist
  - Supports 209 outlets from Kuala Lumpur/Selangor
  - Returns matching outlets with location details
  - Example: `GET /outlets?query=outlets in petaling jaya`
  - Example: `GET /outlets?query=SS2 opening hours`
  - Example: `GET /outlets?query=all outlets` (returns up to 200)

### Chat Agent

- **POST** `/chat`
  - Main multi-agent chat endpoint
  - Handles intent classification, tool calling, and conversation memory
  - **Intent Classification**: LLM-based (Google Gemini) with rule-based fallback
  - **Multi-turn Support**: Tracks conversation history and context
  - Request body:
    ```json
    {
      "message": "What products do you have?",
      "history": [] // Optional, managed by memory manager
    }
    ```
  - Response:
    ```json
    {
      "response": "I found 17 product(s): ...",
      "tool_calls": [
        {
          "tool": "products",
          "input": {"query": "all products"},
          "output": {"success": true, "result": {...}}
        }
      ],
      "intent": "product_search",
      "memory": {
        "slots": {"query": "all products"},
        "context_keys": ["last_outlets"],
        "history_length": 2
      }
    }
    ```

## Data Setup

### Scraping Products

```bash
python scripts/scrape_products.py
```

This scrapes **drinkware only** from `shop.zuscoffee.com` and saves them as JSON files in `data/products/`. The RAG service automatically filters to only "Tumbler" and "Mugs" categories.

**Current Data**: 17 drinkware items (15 Tumblers, 2 Mugs)

### Scraping Outlets

```bash
python scripts/scrape_outlets.py
```

This scrapes outlet information from `zuscoffee.com/category/store/kuala-lumpur-selangor/` and populates the SQLite database at `data/outlets.db`.

**Current Data**: 209 outlets with name, location, district, hours, services, coordinates

### Building FAISS Index

The FAISS index for product search is automatically built when the RAG service is first initialized. Product data should be in `data/products/` before starting the server.

To rebuild the index manually:

```bash
# Via API
curl -X POST http://localhost:8000/products/rebuild-index

# Or restart the server (index rebuilds on first query if missing)
```

## Testing

Run all tests:

```bash
pytest -v
```

Run specific test file:

```bash
pytest tests/test_calculator.py -v
pytest tests/test_products.py -v
pytest tests/test_outlets.py -v
pytest tests/test_agent.py -v
```

Run with coverage:

```bash
pytest --cov=. --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`

## Environment Variables

| Variable         | Description                                | Required |
| ---------------- | ------------------------------------------ | -------- |
| `GEMINI_API_KEY` | Google Gemini API key for LLM and Text2SQL | Yes      |
| `HOST`           | Server host (default: 0.0.0.0)             | No       |
| `PORT`           | Server port (default: 8000)                | No       |
| `ENVIRONMENT`    | Environment mode (development/production)  | No       |

## Key Features & Implementation Details

### Agent Planner

- **Intent Classification**:

  - Primary: LLM-based using Google Gemini (when API key available)
  - Fallback: Rule-based pattern matching
  - Intents: calculator, product_search, outlet_query, general_chat, reset

- **Slot Extraction**:

  - Calculator: extracts mathematical expression
  - Products: extracts search query
  - Outlets: extracts location/outlet name, detects follow-up queries

- **Action Selection**:
  - `ask_clarification`: When required slots are missing
  - `call_calculator`: For calculator intent
  - `call_products`: For product search intent
  - `call_outlets`: For outlet query intent
  - `general_response`: For general chat

### Memory Manager

- **State Tracking**:

  - Slots: Stores extracted slot values (expression, query, etc.)
  - Context: Stores conversation context (last_outlets, etc.)
  - History: Stores conversation messages (limited to 50)

- **Multi-turn Support**:
  - Tracks outlet queries for follow-up questions
  - Example: "Is there an outlet in Petaling Jaya?" → "SS 2, what's the opening time?"

### RAG Service

- **Product Filtering**: Only indexes products with category "Tumbler" or "Mugs"
- **Embeddings**: Uses sentence-transformers "all-MiniLM-L6-v2" model
- **Chunking**: Splits product descriptions into 500-character chunks
- **Search**: Returns top-k results with similarity scores

### Text2SQL Service

- **SQL Injection Protection**:

  - Whitelist: Only allows SELECT queries with safe keywords
  - Blacklist: Blocks DROP, DELETE, UPDATE, INSERT, etc.
  - Quote Escaping: Escapes single quotes in user input

- **Query Generation**:

  - Primary: LangChain SQLDatabaseChain with Google Gemini
  - Fallback: Pattern-based SQL generation for common queries

- **Location Handling**:
  - Location queries (KL, Petaling Jaya, etc.): Returns up to 200 results
  - Specific outlet queries: Returns up to 10 results

### Calculator

- **Security**: Uses `ast.literal_eval` instead of `eval()`
- **Supported Operations**: +, -, \*, /, \*\*, %, unary +/-
- **Error Handling**: Returns structured error messages

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
- **ALWAYS** sanitize SQL queries (whitelist/blacklist + quote escaping)
- **NEVER** expose API keys in code or logs
- **ALWAYS** validate input with Pydantic models

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

1. Ensure product data exists in `data/products/products.json`
2. Restart the server - index will be built on first RAG query
3. Or call `POST /products/rebuild-index` to rebuild manually

### API Key Errors

If you see API key errors:

1. Check `.env` file exists and contains valid `GEMINI_API_KEY`
2. Ensure `.env` is in the `backend/` directory
3. Restart the server after adding/changing API keys

### LLM Not Available

If LLM is not available (no API key):

- Agent planner falls back to rule-based intent classification
- Text2SQL service falls back to pattern-based SQL generation
- System continues to function with reduced accuracy

## Deployment

### Railway/Render

1. Set `GEMINI_API_KEY` environment variable in platform dashboard
2. Ensure `requirements.txt` is in repository
3. Platform will auto-detect FastAPI and run `uvicorn main:app`
4. Health check endpoint: `/health`

### Docker

```bash
# Build image
docker build -t mindhive-backend .

# Run container
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key mindhive-backend
```

Or use `docker-compose.yml` from root directory.

## License

Part of the Mindhive technical assessment project.
