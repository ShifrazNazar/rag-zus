import logging
import asyncio
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


async def execute_tool(
    tool_name: str,
    tool_func: Callable,
    *args,
    **kwargs
) -> Dict[str, Any]:
    try:
        logger.info(f"Executing {tool_name}")
        
        if asyncio.iscoroutinefunction(tool_func):
            result = await tool_func(*args, **kwargs)
        else:
            result = tool_func(*args, **kwargs)
        
        logger.info(f"{tool_name} executed successfully")
        return {
            "success": True,
            "result": result,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"{tool_name} failed: {e}", exc_info=True)
        return {
            "success": False,
            "result": None,
            "error": f"An error occurred: {str(e)}"
        }

