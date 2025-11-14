import logging
import re
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException

from models.schemas import ChatRequest, ChatResponse, ChatMessage, CalculatorRequest
from services.agent_planner import get_agent_planner, AgentPlanner
from services.memory_manager import get_memory_manager
from services.tool_executor import execute_tool

from routers.calculator import calculate as calculate_endpoint
from routers.products import search_products as search_products_endpoint
from routers.outlets import search_outlets as search_outlets_endpoint

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


async def call_calculator(expression: str) -> Dict[str, Any]:
    try:
        request = CalculatorRequest(expression=expression)
        response = await calculate_endpoint(request)
        
        if response.result is not None:
            return {"success": True, "result": response.result}
        else:
            return {"success": False, "error": response.error or "Calculation failed"}
    except Exception as e:
        logger.error(f"Error calling calculator: {e}")
        return {"success": False, "error": str(e)}


async def call_products(query: str) -> Dict[str, Any]:
    try:
        response = await search_products_endpoint(query=query)
        
        result = {
            "results": [
                {
                    "name": p.name,
                    "description": p.description,
                    "price": p.price,
                    "url": p.url
                }
                for p in response.results
            ],
            "summary": response.summary
        }
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error calling products: {e}")
        return {"success": False, "error": str(e)}


async def call_outlets(query: str) -> Dict[str, Any]:
    try:
        response = await search_outlets_endpoint(query=query)
        
        result = {
            "results": [
                {
                    "id": o.id,
                    "name": o.name,
                    "location": o.location,
                    "district": o.district,
                    "hours": o.hours,
                    "services": o.services,
                    "lat": o.lat,
                    "lon": o.lon
                }
                for o in response.results
            ],
            "sql_query": response.sql_query
        }
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error calling outlets: {e}")
        return {"success": False, "error": str(e)}


def format_calculator_response(tool_result: Dict[str, Any]) -> str:
    if tool_result.get("success") and "result" in tool_result:
        result = tool_result["result"]
        return f"The answer is {result}."
    else:
        error = tool_result.get("error", "I couldn't calculate that.")
        return f"Sorry, {error.lower()}"


def format_products_response(tool_result: Dict[str, Any]) -> str:
    if not tool_result.get("success") or "result" not in tool_result:
        error = tool_result.get("error", "I couldn't search for products.")
        return f"Sorry, {error.lower()}"
    
    results = tool_result["result"].get("results", [])
    if not results:
        return "I couldn't find any products matching your search."
    
    response = f"I found {len(results)} product(s):\n"
    for i, product in enumerate(results[:10], 1):
        response += f"{i}. {product.get('name', 'Unknown')}"
        if product.get("price"):
            response += f" - {product.get('price')}"
        response += "\n"
    if len(results) > 10:
        response += f"... and {len(results) - 10} more.\n"
    return response.strip()


def format_outlets_response(tool_result: Dict[str, Any]) -> str:
    if not tool_result.get("success") or "result" not in tool_result:
        error = tool_result.get("error", "I couldn't search for outlets.")
        return f"Sorry, {error.lower()}"
    
    results = tool_result["result"].get("results", [])
    if not results:
        return "I couldn't find any outlets matching your search."
    
    if len(results) == 1:
        outlet = results[0]
        return f"Yes! I found {outlet.get('name', 'Unknown')} at {outlet.get('location', 'Unknown')}. Hours: {outlet.get('hours', 'Not available')}"
    
    # Multiple results - show first 10
    response = f"Yes! I found {len(results)} outlet(s):\n"
    for i, outlet in enumerate(results[:10], 1):
        response += f"{i}. {outlet.get('name', 'Unknown')} - {outlet.get('location', 'Unknown')}\n"
    if len(results) > 10:
        response += f"... and {len(results) - 10} more.\n"
    response += "\nWhich outlet are you referring to?"
    return response


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        session_id = "default"
        
        planner = get_agent_planner()
        memory_manager = get_memory_manager()
        memory = memory_manager.get_memory(session_id)
        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=None
        )
        memory_manager.add_to_history(session_id, user_message)
        
        logger.info(f"Analyzing intent for: {request.message}")
        intent_result = planner.analyze_intent(request.message, memory)
        intent = intent_result.get("intent", AgentPlanner.INTENT_CHAT)
        slots = intent_result.get("slots", {})
        missing_slots = intent_result.get("missing_slots", [])
        
        if intent == AgentPlanner.INTENT_RESET:
            memory_manager.clear_memory(session_id)
            return ChatResponse(
                response="I've cleared our conversation. How can I help you?",
                tool_calls=None,
                intent=intent,
                memory=memory_manager.get_memory_summary(session_id)
            )
        
        action = planner.select_action(intent, slots, missing_slots)
        logger.info(f"Selected action: {action} for intent: {intent}")
        
        if action == "ask_clarification":
            clarification_msg = _get_clarification_message(intent, missing_slots)
            return ChatResponse(
                response=clarification_msg,
                tool_calls=None,
                intent=intent,
                memory=memory_manager.get_memory_summary(session_id)
            )
        
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
            followup = slots.get("followup")
            
            if followup == "hours":
                last_outlets = memory_manager.get_context(session_id, "last_outlets", [])
                outlet_name = query.split('–')[-1].split('-')[-1].strip().rstrip(',').strip()
                
                matched_outlet = _find_best_outlet_match(outlet_name, last_outlets) if last_outlets else None
                
                if not matched_outlet:
                    tool_result = await call_outlets(outlet_name)
                    if tool_result.get("success") and tool_result.get("result", {}).get("results"):
                        outlets = tool_result["result"]["results"]
                        matched_outlet = _find_best_outlet_match(outlet_name, outlets) or (outlets[0] if outlets else None)
                        if outlets:
                            memory_manager.update_context(session_id, "last_outlets", outlets)
                
                if matched_outlet:
                    hours = matched_outlet.get('hours', 'Not available')
                    name = matched_outlet.get('name', outlet_name)
                    response_text = f"Ah yes, the {name} opens at {hours}." if hours != 'Not available' else f"Sorry, I don't have the opening hours for {name}."
                else:
                    response_text = f"Sorry, I couldn't find information about '{outlet_name}'."
                
                tool_calls.append({
                    "tool": "outlets",
                    "input": {"query": query, "followup": "hours"},
                    "output": {"success": True, "result": matched_outlet} if matched_outlet else {"success": False}
                })
            else:
                tool_result = await call_outlets(query)
                tool_calls.append({
                    "tool": "outlets",
                    "input": {"query": query},
                    "output": tool_result
                })
                response_text = format_outlets_response(tool_result)
                
                if tool_result.get("success") and tool_result.get("result", {}).get("results"):
                    outlets = tool_result["result"]["results"]
                    memory_manager.update_context(session_id, "last_outlets", outlets)
                    if len(outlets) > 1:
                        response_text = response_text.rstrip() + "\n\nWhich outlet are you referring to?"
            
        else:
            response_text = _get_general_response(request.message, intent)
        
        assistant_message = ChatMessage(
            role="assistant",
            content=response_text,
            timestamp=None
        )
        memory_manager.add_to_history(session_id, assistant_message)
        
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
    if intent == AgentPlanner.INTENT_CALCULATOR:
        return "What would you like me to calculate? Please provide a mathematical expression."
    elif intent == AgentPlanner.INTENT_PRODUCTS:
        return "What products are you looking for? Please describe what you'd like to find."
    elif intent == AgentPlanner.INTENT_OUTLETS:
        return "Where would you like to find outlets? Please specify a location."
    else:
        return "Could you please provide more details?"


def _find_best_outlet_match(query: str, available_outlets: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Find the best matching outlet from available outlets.
    Handles variations like "SS 2" vs "SS2".
    """
    query_lower = query.lower().strip()
    # Normalize spaces for matching (e.g., "ss 2" -> "ss2")
    query_normalized = query_lower.replace(' ', '')
    
    for outlet in available_outlets:
        outlet_name = outlet.get('name', '').lower()
        outlet_location = outlet.get('location', '').lower()
        outlet_district = outlet.get('district', '').lower()
        
        # Normalize outlet names for comparison
        outlet_name_normalized = outlet_name.replace(' ', '')
        outlet_location_normalized = outlet_location.replace(' ', '')
        
        # Exact match (with or without spaces)
        if (query_lower in outlet_name or query_lower in outlet_location or 
            query_normalized in outlet_name_normalized or query_normalized in outlet_location_normalized or
            query_lower in outlet_district):
            return outlet
    
    return None


def _get_general_response(message: str, intent: str) -> str:
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! I'm here to help you with calculations, product searches, and finding outlets. What would you like to do?"
    
    if any(word in message_lower for word in ['help', 'what can you do', 'capabilities']):
        return """I can help you with:
- Mathematical calculations (e.g., "What's 2 + 2?")
- Searching for products (e.g., "Show me tumblers")
- Finding outlet locations (e.g., "Outlets in Petaling Jaya")

What would you like to do?"""
    
    return "I'm here to help! You can ask me to calculate something, search for products, or find outlet locations. What would you like to do?"

