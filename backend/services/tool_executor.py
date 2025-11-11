"""
Tool executor with error handling, timeout, and retry logic.
Wraps tool calls with proper error handling and circuit breaker pattern.
"""
import logging
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Simple circuit breaker for tool calls."""
    
    def __init__(self, failure_threshold: int = 3, timeout_seconds: int = 60):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Seconds before attempting to close circuit again
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.is_open = False
    
    def record_success(self) -> None:
        """Record successful call."""
        self.failures = 0
        self.is_open = False
        self.last_failure_time = None
    
    def record_failure(self) -> None:
        """Record failed call."""
        self.failures += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failures >= self.failure_threshold:
            self.is_open = True
            logger.warning(f"Circuit breaker opened after {self.failures} failures")
    
    def can_proceed(self) -> bool:
        """Check if call can proceed."""
        if not self.is_open:
            return True
        
        # Check if timeout has passed
        if self.last_failure_time:
            elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
            if elapsed >= self.timeout_seconds:
                logger.info("Circuit breaker attempting to close")
                self.is_open = False
                self.failures = 0
                return True
        
        return False


class ToolExecutor:
    """Executes tool calls with error handling and timeout."""
    
    def __init__(self, timeout_seconds: int = 3, max_retries: int = 1):
        """
        Initialize tool executor.
        
        Args:
            timeout_seconds: Maximum time to wait for tool execution
            max_retries: Maximum number of retries on failure
        """
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def _get_circuit_breaker(self, tool_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for a tool."""
        if tool_name not in self.circuit_breakers:
            self.circuit_breakers[tool_name] = CircuitBreaker()
        return self.circuit_breakers[tool_name]
    
    async def execute(
        self,
        tool_name: str,
        tool_func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a tool with timeout and error handling.
        
        Args:
            tool_name: Name of the tool (for logging and circuit breaker)
            tool_func: Function to execute
            *args: Positional arguments for tool function
            **kwargs: Keyword arguments for tool function
            
        Returns:
            Dictionary with 'success', 'result', and 'error' keys
        """
        circuit_breaker = self._get_circuit_breaker(tool_name)
        
        # Check circuit breaker
        if not circuit_breaker.can_proceed():
            logger.warning(f"Circuit breaker is open for {tool_name}")
            return {
                "success": False,
                "result": None,
                "error": f"{tool_name} is temporarily unavailable. Please try again later."
            }
        
        # Execute with timeout and retries
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Executing {tool_name} (attempt {attempt + 1})")
                
                # Execute with timeout
                if asyncio.iscoroutinefunction(tool_func):
                    result = await asyncio.wait_for(
                        tool_func(*args, **kwargs),
                        timeout=self.timeout_seconds
                    )
                else:
                    # For sync functions, run in executor
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, lambda: tool_func(*args, **kwargs)),
                        timeout=self.timeout_seconds
                    )
                
                # Record success
                circuit_breaker.record_success()
                
                logger.info(f"{tool_name} executed successfully")
                return {
                    "success": True,
                    "result": result,
                    "error": None
                }
                
            except asyncio.TimeoutError:
                logger.warning(f"{tool_name} timed out after {self.timeout_seconds}s")
                if attempt < self.max_retries:
                    continue
                circuit_breaker.record_failure()
                return {
                    "success": False,
                    "result": None,
                    "error": f"{tool_name} timed out. Please try again."
                }
                
            except Exception as e:
                logger.error(f"{tool_name} failed: {e}", exc_info=True)
                if attempt < self.max_retries:
                    logger.info(f"Retrying {tool_name}...")
                    continue
                circuit_breaker.record_failure()
                return {
                    "success": False,
                    "result": None,
                    "error": f"An error occurred while executing {tool_name}: {str(e)}"
                }
        
        # Should not reach here, but just in case
        return {
            "success": False,
            "result": None,
            "error": f"{tool_name} failed after {self.max_retries + 1} attempts"
        }


# Global instance (singleton pattern)
_tool_executor: Optional[ToolExecutor] = None


def get_tool_executor() -> ToolExecutor:
    """Get or create the global tool executor instance."""
    global _tool_executor
    if _tool_executor is None:
        _tool_executor = ToolExecutor()
    return _tool_executor

