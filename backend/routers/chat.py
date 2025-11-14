import logging
import re
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException

from models.schemas import ChatRequest, ChatResponse, ChatMessage, CalculatorRequest
from services.agent_planner import get_agent_planner, AgentPlanner
from services.memory_manager import get_memory_manager

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
    
    MAX_DISPLAY = 15
    response = f"Yes! I found {len(results)} outlet(s):\n"
    for i, outlet in enumerate(results[:MAX_DISPLAY], 1):
        name = outlet.get('name', 'Unknown')
        location = outlet.get('location', 'Unknown')
        if name == location or location in name:
            response += f"{i}. {name}\n"
        else:
            response += f"{i}. {name} - {location}\n"
    if len(results) > MAX_DISPLAY:
        response += f"... and {len(results) - MAX_DISPLAY} more.\n"
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
            logger.info(f"Outlet query: '{query}', followup: '{followup}'")
            
            if followup in ["hours", "open_time", "close_time", "services", "location"]:
                last_outlets = memory_manager.get_context(session_id, "last_outlets", [])
                outlet_name = query
                if '–' in outlet_name:
                    outlet_name = outlet_name.split('–')[-1].strip()
                if '-' in outlet_name and 'zus' not in outlet_name.lower():
                    outlet_name = outlet_name.split('-')[-1].strip()
                outlet_name = outlet_name.rstrip(',').strip()
                
                matched_outlet = _find_best_outlet_match(outlet_name, last_outlets) if last_outlets else None
                
                if not matched_outlet:
                    tool_result = await call_outlets(outlet_name)
                    if tool_result.get("success") and tool_result.get("result", {}).get("results"):
                        outlets = tool_result["result"]["results"]
                        matched_outlet = _find_best_outlet_match(outlet_name, outlets) or (outlets[0] if outlets else None)
                        if outlets:
                            memory_manager.update_context(session_id, "last_outlets", outlets)
                
                if matched_outlet:
                    name = matched_outlet.get('name', outlet_name)
                    if followup == "hours":
                        hours = matched_outlet.get('hours', 'Not available')
                        response_text = f"Ah yes, the {name} opens at {hours}." if hours != 'Not available' else f"Sorry, I don't have the opening hours for {name}."
                    elif followup == "open_time":
                        hours = matched_outlet.get('hours', 'Not available')
                        if hours != 'Not available':
                            opening_time = _extract_opening_time(hours)
                            response_text = f"Ah yes, the {name} opens at {opening_time}." if opening_time else f"Ah yes, the {name} hours are {hours}."
                        else:
                            response_text = f"Sorry, I don't have the opening time for {name}."
                    elif followup == "close_time":
                        hours = matched_outlet.get('hours', 'Not available')
                        if hours != 'Not available':
                            closing_time = _extract_closing_time(hours)
                            response_text = f"Ah yes, the {name} closes at {closing_time}." if closing_time else f"Ah yes, the {name} hours are {hours}."
                        else:
                            response_text = f"Sorry, I don't have the closing time for {name}."
                    elif followup == "services":
                        services = matched_outlet.get('services', 'Not available')
                        if services and services != 'Not available':
                            response_text = f"Yes, the {name} offers: {services}."
                        else:
                            response_text = f"Sorry, I don't have service information for {name}."
                    elif followup == "location":
                        location = matched_outlet.get('location', 'Not available')
                        district = matched_outlet.get('district', '')
                        if location and location != 'Not available':
                            if district and district != location:
                                response_text = f"The {name} is located at {location}, {district}."
                            else:
                                response_text = f"The {name} is located at {location}."
                        else:
                            response_text = f"Sorry, I don't have location information for {name}."
                    else:
                        response_text = f"I found information about {name}."
                else:
                    response_text = f"Sorry, I couldn't find information about '{outlet_name}'."
                
                tool_calls.append({
                    "tool": "outlets",
                    "input": {"query": query, "followup": followup},
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
                        if len(outlets) > 20:
                            response_text = response_text.rstrip() + "\n\nThere are many outlets. Please specify a location (e.g., 'outlets in Petaling Jaya') to narrow down the results."
                        else:
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
    query_lower = query.lower().strip()
    query_normalized = query_lower.replace(' ', '').replace('–', '').replace('-', '')
    query_words = [w for w in query_lower.split() if len(w) > 2 and w not in ['the', 'and', 'for', 'are', 'has', 'have']]
    
    best_match = None
    best_score = 0
    
    for outlet in available_outlets:
        outlet_name = outlet.get('name', '').lower()
        outlet_location = outlet.get('location', '').lower()
        outlet_district = outlet.get('district', '').lower()
        
        # Normalize outlet names for comparison
        outlet_name_normalized = outlet_name.replace(' ', '').replace('–', '').replace('-', '')
        outlet_location_normalized = outlet_location.replace(' ', '').replace('–', '').replace('-', '')
        
        score = 0
        
        if query_lower == outlet_name or query_normalized == outlet_name_normalized:
            score = 100
        elif query_lower in outlet_name or query_normalized in outlet_name_normalized:
            score = 90
        elif query_lower in outlet_location or query_normalized in outlet_location_normalized:
            score = 70
        elif query_lower in outlet_district:
            score = 60
        elif query_words:
            name_matches = sum(1 for word in query_words if word in outlet_name)
            location_matches = sum(1 for word in query_words if word in outlet_location)
            district_matches = sum(1 for word in query_words if word in outlet_district)
            score = (name_matches * 20) + (location_matches * 10) + (district_matches * 5)
        
        if score > best_score:
            best_score = score
            best_match = outlet
    
    return best_match if best_score >= 20 else None


def _extract_opening_time(hours: str) -> Optional[str]:
    if not hours or hours == 'Not available':
        return None
    
    parts = re.split(r'\s*[-–]\s*', hours.strip(), maxsplit=1)
    if len(parts) >= 1:
        opening = parts[0].strip()
        opening = re.sub(r'^(opens?|open\s+at|from)\s*', '', opening, flags=re.IGNORECASE).strip()
        return opening if opening else None
    return None


def _extract_closing_time(hours: str) -> Optional[str]:
    if not hours or hours == 'Not available':
        return None
    
    parts = re.split(r'\s*[-–]\s*', hours.strip(), maxsplit=1)
    if len(parts) >= 2:
        closing = parts[1].strip()
        closing = re.sub(r'^(closes?|close\s+at|until|to)\s*', '', closing, flags=re.IGNORECASE).strip()
        return closing if closing else None
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

