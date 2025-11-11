"""
Calculator router for safe mathematical expression evaluation.
"""
import ast
import operator
import logging
from fastapi import APIRouter, HTTPException
from typing import Any

from models.schemas import CalculatorRequest, CalculatorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calculate", tags=["calculator"])

# Supported operators for safe evaluation
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(node: ast.AST) -> float:
    """
    Safely evaluate an AST node containing only numbers and basic operators.
    
    Args:
        node: AST node to evaluate
        
    Returns:
        Evaluated result as float
        
    Raises:
        ValueError: If node contains unsafe operations or invalid structure
    """
    # Handle numeric constants (Python < 3.8 uses ast.Num, >= 3.8 uses ast.Constant)
    if hasattr(ast, 'Constant') and isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError("Only numeric constants are allowed")
    elif hasattr(ast, 'Num') and isinstance(node, ast.Num):  # Python < 3.8
        return float(node.n)
    elif isinstance(node, ast.BinOp):
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        op = SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        result = op(left, right)
        # Check for division by zero
        if isinstance(node.op, ast.Div) and right == 0:
            raise ZeroDivisionError("Division by zero")
        if isinstance(node.op, ast.FloorDiv) and right == 0:
            raise ZeroDivisionError("Division by zero")
        if isinstance(node.op, ast.Mod) and right == 0:
            raise ZeroDivisionError("Modulo by zero")
        return result
    elif isinstance(node, ast.UnaryOp):
        operand = safe_eval(node.operand)
        op = SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        return op(operand)
    else:
        raise ValueError(f"Unsupported AST node type: {type(node).__name__}")


def evaluate_expression(expression: str) -> float:
    """
    Safely evaluate a mathematical expression string.
    
    Args:
        expression: Mathematical expression as string (e.g., "2 + 2", "10 / 2")
        
    Returns:
        Result of the evaluation
        
    Raises:
        ValueError: If expression is invalid or contains unsafe operations
        ZeroDivisionError: If expression involves division by zero
    """
    # Remove whitespace
    expression = expression.strip()
    
    if not expression:
        raise ValueError("Empty expression")
    
    try:
        # Parse expression into AST
        tree = ast.parse(expression, mode="eval")
        
        # Ensure it's an expression node
        # Check if it's a simple number first
        if hasattr(ast, 'Constant') and isinstance(tree.body, ast.Constant):
            value = tree.body.value
            if isinstance(value, (int, float)):
                return float(value)
        elif hasattr(ast, 'Num') and isinstance(tree.body, ast.Num):  # Python < 3.8
            value = tree.body.n
            if isinstance(value, (int, float)):
                return float(value)
        
        # Check if it's a valid operation
        if not isinstance(tree.body, (ast.BinOp, ast.UnaryOp)):
            raise ValueError("Expression must be a mathematical operation or number")
        
        # Evaluate safely
        result = safe_eval(tree.body)
        return result
        
    except SyntaxError as e:
        raise ValueError(f"Invalid expression syntax: {str(e)}")
    except ZeroDivisionError:
        raise
    except Exception as e:
        raise ValueError(f"Invalid expression: {str(e)}")


@router.post("", response_model=CalculatorResponse)
async def calculate(request: CalculatorRequest) -> CalculatorResponse:
    """
    Evaluate a mathematical expression safely.
    
    Supports basic arithmetic operations: +, -, *, /, //, %, **
    Supports unary operations: +, -
    
    Args:
        request: CalculatorRequest containing the expression to evaluate
        
    Returns:
        CalculatorResponse with result or error message
        
    Example:
        Request: {"expression": "2 + 2"}
        Response: {"result": 4.0, "error": null}
    """
    try:
        logger.info(f"Calculating expression: {request.expression}")
        result = evaluate_expression(request.expression)
        logger.info(f"Calculation result: {result}")
        return CalculatorResponse(result=result, error=None)
        
    except ZeroDivisionError:
        logger.warning(f"Division by zero in expression: {request.expression}")
        return CalculatorResponse(
            result=None,
            error="Division by zero is not allowed"
        )
        
    except ValueError as e:
        logger.warning(f"Invalid expression '{request.expression}': {str(e)}")
        return CalculatorResponse(
            result=None,
            error=f"Invalid expression: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error calculating '{request.expression}': {str(e)}", exc_info=True)
        return CalculatorResponse(
            result=None,
            error="An error occurred while evaluating the expression"
        )

