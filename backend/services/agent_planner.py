"""
Agent planner for intent classification and action selection.
Uses LLM to classify user intent and select appropriate tools.
"""
import logging
import re
from typing import Dict, Any, Optional, List

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    ChatOpenAI = None
    ChatPromptTemplate = None

logger = logging.getLogger(__name__)


class AgentPlanner:
    """Plans agent actions based on user intent."""
    
    # Intent types
    INTENT_CALCULATOR = "calculator"
    INTENT_PRODUCTS = "product_search"
    INTENT_OUTLETS = "outlet_query"
    INTENT_CHAT = "general_chat"
    INTENT_RESET = "reset"
    
    def __init__(self):
        """Initialize agent planner."""
        self.llm: Optional[ChatOpenAI] = None
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize LLM for intent classification."""
        if ChatOpenAI is None:
            logger.warning("LangChain not available, using rule-based intent classification")
            return
        
        try:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
                verbose=False
            )
            logger.info("Agent planner initialized with LLM")
        except Exception as e:
            logger.warning(f"Could not initialize LLM: {e}. Using fallback.")
            self.llm = None
    
    def analyze_intent(self, user_input: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user intent from input.
        
        Args:
            user_input: User's message
            memory: Current conversation memory
            
        Returns:
            Dictionary with 'intent', 'confidence', and 'slots'
        """
        user_lower = user_input.lower().strip()
        
        # Check for reset command
        if any(word in user_lower for word in ['reset', 'clear', 'start over', 'new conversation']):
            return {
                "intent": self.INTENT_RESET,
                "confidence": 0.9,
                "slots": {},
                "missing_slots": []
            }
        
        # Use LLM if available, otherwise use rule-based
        if self.llm is not None:
            return self._llm_classify_intent(user_input, memory)
        else:
            return self._rule_based_classify_intent(user_input, memory)
    
    def _llm_classify_intent(self, user_input: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        """Classify intent using LLM."""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an intent classifier for a chatbot. Classify the user's intent into one of:
- calculator: User wants to perform a mathematical calculation
- product_search: User wants to search for products
- outlet_query: User wants to find outlet locations
- general_chat: General conversation, greetings, questions

Respond with JSON: {{"intent": "intent_name", "confidence": 0.0-1.0, "slots": {{"key": "value"}}}}"""),
                ("user", user_input)
            ])
            
            chain = prompt | self.llm
            response = chain.invoke({"input": user_input})
            
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
        """Classify intent using rule-based patterns."""
        user_lower = user_input.lower()
        
        # Calculator patterns
        calc_patterns = [
            r'\d+\s*[+\-*/]\s*\d+',  # "2 + 2"
            r'calculate|compute|what is|what\'s|math|arithmetic',
            r'\+|\-|\*|/|plus|minus|times|divided'
        ]
        if any(re.search(pattern, user_lower) for pattern in calc_patterns):
            # Extract expression
            expression = self._extract_expression(user_input)
            return {
                "intent": self.INTENT_CALCULATOR,
                "confidence": 0.8,
                "slots": {"expression": expression} if expression else {},
                "missing_slots": ["expression"] if not expression else []
            }
        
        # Product search patterns
        product_patterns = [
            r'product|item|merchandise|buy|purchase|shop|store',
            r'tumbler|mug|bottle|drinkware|coffee cup'
        ]
        if any(re.search(pattern, user_lower) for pattern in product_patterns):
            # Extract product query
            query = self._extract_product_query(user_input)
            return {
                "intent": self.INTENT_PRODUCTS,
                "confidence": 0.8,
                "slots": {"query": query} if query else {},
                "missing_slots": ["query"] if not query else []
            }
        
        # Outlet query patterns
        outlet_patterns = [
            r'outlet|location|store|branch|where|find|near|nearby',
            r'petaling jaya|kl|kuala lumpur|selangor|pj'
        ]
        if any(re.search(pattern, user_lower) for pattern in outlet_patterns):
            # Extract location query
            query = self._extract_location_query(user_input)
            return {
                "intent": self.INTENT_OUTLETS,
                "confidence": 0.8,
                "slots": {"query": query} if query else {},
                "missing_slots": ["query"] if not query else []
            }
        
        # Default to general chat
        return {
            "intent": self.INTENT_CHAT,
            "confidence": 0.5,
            "slots": {},
            "missing_slots": []
        }
    
    def _extract_expression(self, text: str) -> Optional[str]:
        """Extract mathematical expression from text."""
        # Simple extraction - look for patterns like "2 + 2" or "calculate 10 * 5"
        patterns = [
            r'(\d+\s*[+\-*/]\s*\d+)',
            r'calculate\s+(.+)',
            r'what is\s+(.+)',
            r'what\'s\s+(.+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if len(match.groups()) > 0 else match.group(0)
        return None
    
    def _extract_product_query(self, text: str) -> Optional[str]:
        """Extract product search query from text."""
        # Remove common phrases
        text = re.sub(r'(show|find|search|what|do you have|products?|items?)', '', text, flags=re.IGNORECASE)
        text = text.strip()
        return text if len(text) > 2 else None
    
    def _extract_location_query(self, text: str) -> Optional[str]:
        """Extract location query from text."""
        # Remove common phrases
        text = re.sub(r'(find|where|outlets?|locations?|stores?|branches?)', '', text, flags=re.IGNORECASE)
        text = text.strip()
        return text if len(text) > 2 else text or "all"
    
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

