from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from routers import calculator, products, outlets, chat
from models.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mindhive AI Chatbot API",
    description="Multi-agent chatbot with RAG, Text2SQL, and tool calling",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(calculator.router)
app.include_router(products.router)
app.include_router(outlets.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {"message": "Mindhive AI Chatbot API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mindhive-chatbot"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "An unexpected error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
