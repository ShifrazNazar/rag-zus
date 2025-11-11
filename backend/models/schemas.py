"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class CalculatorRequest(BaseModel):
    """Request model for calculator endpoint."""
    expression: str = Field(..., description="Mathematical expression to evaluate")


class CalculatorResponse(BaseModel):
    """Response model for calculator endpoint."""
    result: Optional[float] = None
    error: Optional[str] = None


class ProductsRequest(BaseModel):
    """Request model for products search."""
    query: str = Field(..., min_length=1, description="Search query for products")


class ProductResult(BaseModel):
    """Single product result."""
    name: str
    description: str
    price: Optional[str] = None
    url: Optional[str] = None


class ProductsResponse(BaseModel):
    """Response model for products search."""
    results: List[ProductResult] = Field(default_factory=list)
    summary: Optional[str] = None


class OutletsRequest(BaseModel):
    """Request model for outlets search."""
    query: str = Field(..., min_length=1, description="Natural language query for outlets")


class OutletResult(BaseModel):
    """Single outlet result."""
    id: int
    name: str
    location: str
    district: Optional[str] = None
    hours: Optional[str] = None
    services: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


class OutletsResponse(BaseModel):
    """Response model for outlets search."""
    results: List[OutletResult] = Field(default_factory=list)
    sql_query: Optional[str] = None


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, description="User message")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Conversation history")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    intent: Optional[str] = None
    memory: Optional[Dict[str, Any]] = None

