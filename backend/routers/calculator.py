import ast
import operator
import logging
from fastapi import APIRouter, HTTPException
from models.schemas import CalculatorRequest, CalculatorResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/calculate", tags=["calculator"])

SAFE_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def safe_eval(node: ast.AST) -> float:
    if isinstance(node, (ast.Constant if hasattr(ast, 'Constant') else type(None))) and hasattr(node, 'value'):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError("Only numeric constants are allowed")
    elif hasattr(ast, 'Num') and isinstance(node, ast.Num):
        return float(node.n)
    elif isinstance(node, ast.BinOp):
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        op = SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator")
        if right == 0 and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
            raise ZeroDivisionError("Division by zero")
        return op(left, right)
    elif isinstance(node, ast.UnaryOp):
        return SAFE_OPERATORS.get(type(node.op), lambda x: x)(safe_eval(node.operand))
    else:
        raise ValueError(f"Unsupported node type")


def evaluate_expression(expression: str) -> float:
    expression = expression.strip()
    if not expression:
        raise ValueError("Empty expression")
    
    try:
        tree = ast.parse(expression, mode="eval")
        body = tree.body
        
        if isinstance(body, (ast.Constant if hasattr(ast, 'Constant') else type(None))) and hasattr(body, 'value'):
            if isinstance(body.value, (int, float)):
                return float(body.value)
        elif hasattr(ast, 'Num') and isinstance(body, ast.Num):
            return float(body.n)
        
        if not isinstance(body, (ast.BinOp, ast.UnaryOp)):
            raise ValueError("Expression must be a mathematical operation or number")
        
        return safe_eval(body)
    except (SyntaxError, ZeroDivisionError) as e:
        raise
    except Exception as e:
        raise ValueError(f"Invalid expression: {str(e)}")


@router.post("", response_model=CalculatorResponse)
async def calculate(request: CalculatorRequest) -> CalculatorResponse:
    try:
        result = evaluate_expression(request.expression)
        return CalculatorResponse(result=result, error=None)
    except ZeroDivisionError:
        return CalculatorResponse(result=None, error="Division by zero is not allowed")
    except ValueError as e:
        return CalculatorResponse(result=None, error=f"Invalid expression: {str(e)}")
    except Exception as e:
        logger.error(f"Error calculating: {e}", exc_info=True)
        return CalculatorResponse(result=None, error="An error occurred while evaluating the expression")
