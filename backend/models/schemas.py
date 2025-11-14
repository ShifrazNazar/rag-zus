from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class CalculatorRequest(BaseModel):
    expression: str = Field(..., description="Mathematical expression to evaluate")


class CalculatorResponse(BaseModel):
    result: Optional[float] = None
    error: Optional[str] = None


class ProductResult(BaseModel):
    name: str
    description: str
    price: Optional[str] = None
    url: Optional[str] = None


class ProductsResponse(BaseModel):
    results: List[ProductResult] = Field(default_factory=list)
    summary: Optional[str] = None


class OutletResult(BaseModel):
    id: int
    name: str
    location: str
    district: Optional[str] = None
    hours: Optional[str] = None
    services: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class OutletsResponse(BaseModel):
    results: List[OutletResult] = Field(default_factory=list)
    sql_query: Optional[str] = None


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Conversation history")


class ChatResponse(BaseModel):
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    intent: Optional[str] = None
    memory: Optional[Dict[str, Any]] = None
