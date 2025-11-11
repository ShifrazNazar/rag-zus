"""
Chat router for main multi-agent chat endpoint.
Orchestrates intent classification, tool calling, and response generation.
"""
import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException

try:
    import httpx
except ImportError:
    httpx = None

from models.schemas import ChatRequest, ChatResponse, ChatMessage
from services.agent_planner import get_agent_planner, AgentPlanner
from services.memory_manager import get_memory_manager
from services.tool_executor import get_tool_executor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Base URL for internal API calls
BASE_URL = "http://localhost:8000"


async def call_calculator(expression: str) -> Dict[str, Any]:
    """Call calculator endpoint."""
    if httpx is None:
        return {"success": False, "error": "httpx not available"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/calculate",
                json={"expression": expression},
                timeout=3.0
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("result") is not None:
                    return {"success": True, "result": data["result"]}
                else:
                    return {"success": False, "error": data.get("error", "Calculation failed")}
            return {"success": False, "error": "Calculator service error"}
        except Exception as e:
            logger.error(f"Error calling calculator: {e}")
            return {"success": False, "error": str(e)}


async def call_products(query: str) -> Dict[str, Any]:
    """Call products search endpoint."""
    if httpx is None:
        return {"success": False, "error": "httpx not available"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/products",
                params={"query": query},
                timeout=3.0
            )
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "result": data}
            return {"success": False, "error": "Products service error"}
        except Exception as e:
            logger.error(f"Error calling products: {e}")
            return {"success": False, "error": str(e)}


async def call_outlets(query: str) -> Dict[str, Any]:
    """Call outlets search endpoint."""
    if httpx is None:
        return {"success": False, "error": "httpx not available"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/outlets",
                params={"query": query},
                timeout=3.0
            )
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "result": data}
            return {"success": False, "error": "Outlets service error"}
        except Exception as e:
            logger.error(f"Error calling outlets: {e}")
            return {"success": False, "error": str(e)}


def format_calculator_response(tool_result: Dict[str, Any]) -> str:
    """Format calculator tool result into user-friendly response."""
    if tool_result.get("success") and "result" in tool_result:
        result = tool_result["result"]
        return f"The answer is {result}."
    else:
        error = tool_result.get("error", "I couldn't calculate that.")
        return f"Sorry, {error.lower()}"


def format_products_response(tool_result: Dict[str, Any]) -> str:
    """Format products search result into user-friendly response."""
    if tool_result.get("success") and "result" in tool_result:
        data = tool_result["result"]
        results = data.get("results", [])
        if results:
            product_names = [p.get("name", "Unknown") for p in results[:3]]
            response = f"I found {len(results)} product(s):\n"
            for i, product in enumerate(results[:3], 1):
                response += f"{i}. {product.get('name', 'Unknown')}"
                if product.get("price"):
                    response += f" - {product.get('price')}"
                response += "\n"
            if data.get("summary"):
                response += f"\n{data['summary']}"
            return response
        else:
            return "I couldn't find any products matching your search."
    else:
        error = tool_result.get("error", "I couldn't search for products.")
        return f"Sorry, {error.lower()}"


def format_outlets_response(tool_result: Dict[str, Any]) -> str:
    """Format outlets search result into user-friendly response."""
    if tool_result.get("success") and "result" in tool_result:
        data = tool_result["result"]
        results = data.get("results", [])
        if results:
            response = f"I found {len(results)} outlet(s):\n"
            for i, outlet in enumerate(results[:5], 1):
                response += f"{i}. {outlet.get('name', 'Unknown')} - {outlet.get('location', 'Unknown location')}"
                if outlet.get("district"):
                    response += f" ({outlet.get('district')})"
                response += "\n"
            return response
        else:
            return "I couldn't find any outlets matching your search."
    else:
        error = tool_result.get("error", "I couldn't search for outlets.")
        return f"Sorry, {error.lower()}"


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for multi-agent conversation.
    
    Handles intent classification, tool calling, and response generation.
    
    Args:
        request: ChatRequest with user message and history
        
    Returns:
        ChatResponse with agent's response and metadata
    """
    try:
        # Generate session ID from request (in production, use proper session management)
        session_id = "default"  # Could be extracted from headers or request
        
        # Get services
        planner = get_agent_planner()
        memory_manager = get_memory_manager()
        tool_executor = get_tool_executor()
        
        # Get memory
        memory = memory_manager.get_memory(session_id)
        
        # Add user message to history
        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=None
        )
        memory_manager.add_to_history(session_id, user_message)
        
        # Analyze intent
        logger.info(f"Analyzing intent for: {request.message}")
        intent_result = planner.analyze_intent(request.message, memory)
        intent = intent_result.get("intent", AgentPlanner.INTENT_CHAT)
        slots = intent_result.get("slots", {})
        missing_slots = intent_result.get("missing_slots", [])
        
        # Handle reset
        if intent == AgentPlanner.INTENT_RESET:
            memory_manager.clear_memory(session_id)
            return ChatResponse(
                response="I've cleared our conversation. How can I help you?",
                tool_calls=None,
                intent=intent,
                memory=memory_manager.get_memory_summary(session_id)
            )
        
        # Select action
        action = planner.select_action(intent, slots, missing_slots)
        logger.info(f"Selected action: {action} for intent: {intent}")
        
        # Handle clarification needed
        if action == "ask_clarification":
            clarification_msg = _get_clarification_message(intent, missing_slots)
            return ChatResponse(
                response=clarification_msg,
                tool_calls=None,
                intent=intent,
                memory=memory_manager.get_memory_summary(session_id)
            )
        
        # Execute tool calls
        tool_calls = []
        response_text = ""
        
        if action == "call_calculator":
            expression = slots.get("expression", request.message)
            tool_result = await call_calculator(expression)
            tool_calls.append({
                "tool": "calculator",
                "input": {"expression": expression},
                "output": tool_result
            })
            response_text = format_calculator_response(tool_result)
            
        elif action == "call_products":
            query = slots.get("query", request.message)
            tool_result = await call_products(query)
            tool_calls.append({
                "tool": "products",
                "input": {"query": query},
                "output": tool_result
            })
            response_text = format_products_response(tool_result)
            
        elif action == "call_outlets":
            query = slots.get("query", request.message)
            tool_result = await call_outlets(query)
            tool_calls.append({
                "tool": "outlets",
                "input": {"query": query},
                "output": tool_result
            })
            response_text = format_outlets_response(tool_result)
            
        else:
            # General chat response
            response_text = _get_general_response(request.message, intent)
        
        # Add assistant message to history
        assistant_message = ChatMessage(
            role="assistant",
            content=response_text,
            timestamp=None
        )
        memory_manager.add_to_history(session_id, assistant_message)
        
        # Update memory slots
        for key, value in slots.items():
            memory_manager.update_slot(session_id, key, value)
        
        logger.info(f"Generated response for intent: {intent}")
        
        return ChatResponse(
            response=response_text,
            tool_calls=tool_calls if tool_calls else None,
            intent=intent,
            memory=memory_manager.get_memory_summary(session_id)
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your message"
        )


def _get_clarification_message(intent: str, missing_slots: List[str]) -> str:
    """Generate clarification message for missing slots."""
    if intent == AgentPlanner.INTENT_CALCULATOR:
        return "What would you like me to calculate? Please provide a mathematical expression."
    elif intent == AgentPlanner.INTENT_PRODUCTS:
        return "What products are you looking for? Please describe what you'd like to find."
    elif intent == AgentPlanner.INTENT_OUTLETS:
        return "Where would you like to find outlets? Please specify a location."
    else:
        return "Could you please provide more details?"


def _get_general_response(message: str, intent: str) -> str:
    """Generate general chat response."""
    message_lower = message.lower()
    
    # Greetings
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! I'm here to help you with calculations, product searches, and finding outlets. What would you like to do?"
    
    # Help
    if any(word in message_lower for word in ['help', 'what can you do', 'capabilities']):
        return """I can help you with:
- Mathematical calculations (e.g., "What's 2 + 2?")
- Searching for products (e.g., "Show me tumblers")
- Finding outlet locations (e.g., "Outlets in Petaling Jaya")

What would you like to do?"""
    
    # Default
    return "I'm here to help! You can ask me to calculate something, search for products, or find outlet locations. What would you like to do?"

