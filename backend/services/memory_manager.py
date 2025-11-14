import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from models.schemas import ChatMessage

logger = logging.getLogger(__name__)


class MemoryManager:
    def __init__(self):
        self.memories: Dict[str, Dict[str, Any]] = {}
    
    def get_memory(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.memories:
            self.memories[session_id] = {
                "slots": {},
                "context": {},
                "history": [],
                "last_updated": datetime.utcnow().isoformat()
            }
        return self.memories[session_id]
    
    def update_slot(self, session_id: str, slot_name: str, value: Any) -> None:
        memory = self.get_memory(session_id)
        memory["slots"][slot_name] = value
        memory["last_updated"] = datetime.utcnow().isoformat()
        logger.info(f"Updated slot {slot_name} for session {session_id}")
    
    def get_slot(self, session_id: str, slot_name: str, default: Any = None) -> Any:
        memory = self.get_memory(session_id)
        return memory["slots"].get(slot_name, default)
    
    def update_context(self, session_id: str, key: str, value: Any) -> None:
        memory = self.get_memory(session_id)
        memory["context"][key] = value
        memory["last_updated"] = datetime.utcnow().isoformat()
        logger.info(f"Updated context {key} for session {session_id}")
    
    def get_context(self, session_id: str, key: str, default: Any = None) -> Any:
        memory = self.get_memory(session_id)
        return memory["context"].get(key, default)
    
    def add_to_history(self, session_id: str, message: ChatMessage) -> None:
        memory = self.get_memory(session_id)
        memory["history"].append({
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp or datetime.utcnow().isoformat()
        })
        if len(memory["history"]) > 50:
            memory["history"] = memory["history"][-50:]
        memory["last_updated"] = datetime.utcnow().isoformat()
    
    def get_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        memory = self.get_memory(session_id)
        history = memory["history"]
        if limit:
            return history[-limit:]
        return history
    
    def clear_memory(self, session_id: str) -> None:
        if session_id in self.memories:
            self.memories[session_id] = {
                "slots": {},
                "context": {},
                "history": [],
                "last_updated": datetime.utcnow().isoformat()
            }
            logger.info(f"Cleared memory for session {session_id}")
    
    def get_memory_summary(self, session_id: str) -> Dict[str, Any]:
        memory = self.get_memory(session_id)
        return {
            "slots": memory["slots"],
            "context_keys": list(memory["context"].keys()),
            "history_length": len(memory["history"]),
            "last_updated": memory["last_updated"]
        }


_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
