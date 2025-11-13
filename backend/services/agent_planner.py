import os
import logging
import re
from typing import Dict, Any, Optional, List, Union

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.language_models import BaseChatModel
except ImportError:
    ChatGoogleGenerativeAI = None
    ChatPromptTemplate = None
    BaseChatModel = None

logger = logging.getLogger(__name__)


class AgentPlanner:
    
    INTENT_CALCULATOR = "calculator"
    INTENT_PRODUCTS = "product_search"
    INTENT_OUTLETS = "outlet_query"
    INTENT_CHAT = "general_chat"
    INTENT_RESET = "reset"
    
    def __init__(self):
        self.llm: Optional[BaseChatModel] = None
        self._initialize()
    
    def _initialize(self) -> None:
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if gemini_key and ChatGoogleGenerativeAI is not None:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    temperature=0,
                    google_api_key=gemini_key
                )
                logger.info("Agent planner initialized with Google Gemini")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini: {e}")
                self.llm = None
        else:
            if not gemini_key:
                logger.warning("GEMINI_API_KEY not found in environment variables")
            if ChatGoogleGenerativeAI is None:
                logger.warning("langchain_google_genai not available")
            self.llm = None
        
        if self.llm is None:
            logger.warning("No LLM available, using rule-based intent classification")
    
    def analyze_intent(self, user_input: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        user_lower = user_input.lower().strip()
        
        if any(word in user_lower for word in ['reset', 'clear', 'start over', 'new conversation']):
            return {
                "intent": self.INTENT_RESET,
                "confidence": 0.9,
                "slots": {},
                "missing_slots": []
            }
        
        return self._rule_based_classify_intent(user_input, memory)
    
    def _llm_classify_intent(self, user_input: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        try:
            last_outlets = memory.get("context", {}).get("last_outlets", [])
            context_info = ""
            if last_outlets:
                outlet_names = [o.get('name', '') for o in last_outlets[:3]]
                context_info = f"\n\nPrevious context: User recently asked about outlets: {', '.join(outlet_names)}"
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""You are an intent classifier for a chatbot. Classify the user's intent into one of:
- calculator: User wants to perform a mathematical calculation
- product_search: User wants to search for products
- outlet_query: User wants to find outlet locations or ask about specific outlets (opening hours, details)
- general_chat: General conversation, greetings, questions

If the user is asking about opening hours, times, or details of a specific outlet mentioned in previous context, classify as outlet_query with followup: "hours" in slots.
If the user mentions a location like "Petaling Jaya", "SS 2", "1 Utama", classify as outlet_query.{context_info}

Respond with JSON: {{"intent": "intent_name", "confidence": 0.0-1.0, "slots": {{"key": "value", "followup": "hours" if asking about opening times}}}}"""),
                ("user", "{user_input}")
            ])
            
            chain = prompt | self.llm
            response = chain.invoke({"user_input": user_input})
            
            # Parse response (simplified - in production, use structured output)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Try to extract JSON
            import json
            try:
                # Find JSON in response
                json_match = re.search(r'\{[^}]+\}', content)
                if json_match:
                    result = json.loads(json_match.group())
                    return {
                        "intent": result.get("intent", self.INTENT_CHAT),
                        "confidence": result.get("confidence", 0.5),
                        "slots": result.get("slots", {}),
                        "missing_slots": []
                    }
            except:
                pass
            
            # Fallback to rule-based
            return self._rule_based_classify_intent(user_input, memory)
            
        except Exception as e:
            logger.error(f"Error in LLM intent classification: {e}", exc_info=True)
            return self._rule_based_classify_intent(user_input, memory)
    
    def _rule_based_classify_intent(self, user_input: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['hour', 'time', 'open', 'close', 'when', 'opening']):
            last_outlets = memory.get("context", {}).get("last_outlets", [])
            if last_outlets:
                outlet_name = self._extract_outlet_name(user_input, last_outlets)
                if outlet_name:
                    return {
                        "intent": self.INTENT_OUTLETS,
                        "confidence": 0.9,
                        "slots": {"query": outlet_name, "followup": "hours"},
                        "missing_slots": []
                    }
        
        if re.search(r'\d+\s*[+\-*/]\s*\d+|calculate|compute|what is|what\'s|math|\+|\-|\*|/|plus|minus|times', user_lower):
            expression = self._extract_expression(user_input)
            return {
                "intent": self.INTENT_CALCULATOR,
                "confidence": 0.8,
                "slots": {"expression": expression} if expression else {},
                "missing_slots": ["expression"] if not expression else []
            }
        
        if re.search(r'product|item|tumbler|mug|bottle|drinkware|buy|purchase', user_lower):
            query = self._extract_product_query(user_input)
            return {
                "intent": self.INTENT_PRODUCTS,
                "confidence": 0.8,
                "slots": {"query": query} if query else {},
                "missing_slots": ["query"] if not query else []
            }
        
        if re.search(r'outlet|location|store|where|find|near|petaling jaya|kl|kuala lumpur|selangor', user_lower):
            query = self._extract_location_query(user_input)
            if 'near me' in user_lower or 'all outlets' in user_lower:
                query = "all outlets"
            return {
                "intent": self.INTENT_OUTLETS,
                "confidence": 0.8,
                "slots": {"query": query} if query else {},
                "missing_slots": ["query"] if not query else []
            }
        
        return {
            "intent": self.INTENT_CHAT,
            "confidence": 0.5,
            "slots": {},
            "missing_slots": []
        }
    
    def _extract_expression(self, text: str) -> Optional[str]:
        match = re.search(r'(\d+\s*[+\-*/]\s*\d+)|calculate\s+(.+)|what is\s+(.+)|what\'s\s+(.+)', text, re.IGNORECASE)
        if match:
            return match.group(1) or match.group(2) or match.group(3) or match.group(4)
        return None
    
    def _extract_product_query(self, text: str) -> Optional[str]:
        text_lower = text.lower().strip()
        if re.match(r'^(show|find|list|what|do you have|get|see)\s+(me\s+)?(all\s+)?(products?|items?)$', text_lower):
            return "all products"
        text = re.sub(r'^(show|find|search|what|do you have|get|see|list)\s+(me\s+)?|\s+(products?|items?)$', '', text, flags=re.IGNORECASE).strip()
        return text if text else None
    
    def _extract_location_query(self, text: str) -> Optional[str]:
        text = re.sub(r'(find|where|outlets?|locations?|stores?|branches?)', '', text, flags=re.IGNORECASE).strip()
        return text if len(text) > 2 else "all"
    
    def _extract_outlet_name(self, text: str, available_outlets: List[Dict[str, Any]]) -> Optional[str]:
        text_lower = text.lower()
        
        # First, try to extract full outlet name pattern "ZUS Coffee – [Name]"
        full_outlet_pattern = r'zus\s+coffee\s*[–\-]\s*([^,?\n]+)'
        match = re.search(full_outlet_pattern, text_lower, re.IGNORECASE)
        if match:
            extracted_name = match.group(1).strip()
            # If we have available outlets, try to find exact or best match
            if available_outlets:
                best_match = self._find_best_outlet_match(extracted_name, available_outlets)
                if best_match:
                    return best_match.get('name', extracted_name)
            # Return the extracted name (will be used in query)
            return extracted_name
        
        # Common outlet name patterns (short names)
        outlet_patterns = [
            r'(ss\s*2|ss2)',
            r'(1\s*utama|1utama)',
            r'(klcc)',
            r'(pavilion)',
            r'(sunway\s*pyramid|sunway)',
            r'(subang\s*jaya|subang)',
            r'(damansara\s*perdana|damansara)'
        ]
        
        # Try to match short patterns
        for pattern in outlet_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                matched_text = match.group(1).strip()
                
                # Normalize outlet names
                if 'ss' in matched_text or 'ss2' in matched_text:
                    # Look for SS 2 in available outlets
                    if available_outlets:
                        for outlet in available_outlets:
                            outlet_name_lower = outlet.get('name', '').lower()
                            if 'ss' in outlet_name_lower and '2' in outlet_name_lower:
                                return outlet.get('name', matched_text)
                    return "SS 2"
                elif 'utama' in matched_text:
                    if available_outlets:
                        for outlet in available_outlets:
                            if 'utama' in outlet.get('name', '').lower():
                                return outlet.get('name', matched_text)
                    return "1 Utama"
                elif 'klcc' in matched_text:
                    if available_outlets:
                        for outlet in available_outlets:
                            if 'klcc' in outlet.get('name', '').lower():
                                return outlet.get('name', matched_text)
                    return "KLCC"
                elif 'pavilion' in matched_text:
                    if available_outlets:
                        for outlet in available_outlets:
                            if 'pavilion' in outlet.get('name', '').lower():
                                return outlet.get('name', matched_text)
                    return "Pavilion"
                elif 'sunway' in matched_text:
                    if available_outlets:
                        for outlet in available_outlets:
                            if 'sunway' in outlet.get('name', '').lower():
                                return outlet.get('name', matched_text)
                    return "Sunway Pyramid"
                elif 'subang' in matched_text:
                    if available_outlets:
                        for outlet in available_outlets:
                            if 'subang' in outlet.get('name', '').lower():
                                return outlet.get('name', matched_text)
                    return "Subang Jaya"
                elif 'damansara' in matched_text:
                    if available_outlets:
                        for outlet in available_outlets:
                            if 'damansara' in outlet.get('name', '').lower():
                                return outlet.get('name', matched_text)
                    return "Damansara Perdana"
        
        # If we have available outlets, try fuzzy matching with better scoring
        if available_outlets:
            # Extract potential outlet name (remove common question words)
            cleaned = re.sub(r'(what|what\'s|the|opening|hours?|time|when|is|there|an|outlet|in|zus\s+coffee)', '', text_lower, flags=re.IGNORECASE)
            cleaned = cleaned.strip().strip('–-,').strip()
            
            if cleaned:
                best_match = self._find_best_outlet_match(cleaned, available_outlets)
                if best_match:
                    return best_match.get('name', cleaned)
        
        return None
    
    def _find_best_outlet_match(self, query: str, available_outlets: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Find the best matching outlet from available outlets based on query.
        Uses scoring to find the most relevant match.
        
        Args:
            query: Query text to match against
            available_outlets: List of available outlet dictionaries
            
        Returns:
            Best matching outlet dictionary or None
        """
        query_lower = query.lower().strip()
        query_words = set(word for word in query_lower.split() if len(word) > 2)
        
        best_match = None
        best_score = 0
        
        for outlet in available_outlets:
            outlet_name = outlet.get('name', '').lower()
            outlet_location = outlet.get('location', '').lower()
            
            score = 0
            
            # Exact match gets highest score
            if query_lower in outlet_name:
                score = 100
            elif query_lower in outlet_location:
                score = 80
            # Check if all query words are in outlet name (high score)
            elif query_words and all(word in outlet_name for word in query_words):
                score = 70 + len(query_words) * 5
            # Check if all query words are in location
            elif query_words and all(word in outlet_location for word in query_words):
                score = 50 + len(query_words) * 5
            # Partial word matches (lower score)
            elif query_words:
                name_matches = sum(1 for word in query_words if word in outlet_name)
                location_matches = sum(1 for word in query_words if word in outlet_location)
                score = (name_matches * 10) + (location_matches * 5)
            
            if score > best_score:
                best_score = score
                best_match = outlet
        
        # Only return match if score is above threshold
        return best_match if best_score >= 20 else None
    
    def select_action(self, intent: str, slots: Dict[str, Any], missing_slots: List[str]) -> str:
        """
        Select action based on intent and slots.
        
        Args:
            intent: Detected intent
            slots: Extracted slots
            missing_slots: List of missing required slots
            
        Returns:
            Action name
        """
        if intent == self.INTENT_RESET:
            return "reset_memory"
        
        if missing_slots:
            return "ask_clarification"
        
        if intent == self.INTENT_CALCULATOR:
            return "call_calculator"
        elif intent == self.INTENT_PRODUCTS:
            return "call_products"
        elif intent == self.INTENT_OUTLETS:
            return "call_outlets"
        else:
            return "general_response"


# Global instance (singleton pattern)
_agent_planner: Optional[AgentPlanner] = None


def get_agent_planner() -> AgentPlanner:
    """Get or create the global agent planner instance."""
    global _agent_planner
    if _agent_planner is None:
        _agent_planner = AgentPlanner()
    return _agent_planner

