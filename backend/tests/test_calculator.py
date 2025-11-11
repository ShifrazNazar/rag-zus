"""
Tests for calculator endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_calculate_addition():
    """Test basic addition."""
    response = client.post(
        "/calculate",
        json={"expression": "2 + 2"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 4.0
    assert data["error"] is None


def test_calculate_subtraction():
    """Test basic subtraction."""
    response = client.post(
        "/calculate",
        json={"expression": "10 - 3"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 7.0
    assert data["error"] is None


def test_calculate_multiplication():
    """Test basic multiplication."""
    response = client.post(
        "/calculate",
        json={"expression": "5 * 4"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 20.0
    assert data["error"] is None


def test_calculate_division():
    """Test basic division."""
    response = client.post(
        "/calculate",
        json={"expression": "10 / 2"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 5.0
    assert data["error"] is None


def test_calculate_floor_division():
    """Test floor division."""
    response = client.post(
        "/calculate",
        json={"expression": "10 // 3"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 3.0
    assert data["error"] is None


def test_calculate_modulo():
    """Test modulo operation."""
    response = client.post(
        "/calculate",
        json={"expression": "10 % 3"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 1.0
    assert data["error"] is None


def test_calculate_power():
    """Test power operation."""
    response = client.post(
        "/calculate",
        json={"expression": "2 ** 3"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 8.0
    assert data["error"] is None


def test_calculate_complex_expression():
    """Test complex expression with multiple operations."""
    response = client.post(
        "/calculate",
        json={"expression": "2 + 3 * 4 - 1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 13.0  # 2 + 12 - 1
    assert data["error"] is None


def test_calculate_negative_number():
    """Test negative number."""
    response = client.post(
        "/calculate",
        json={"expression": "-5"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == -5.0
    assert data["error"] is None


def test_calculate_unary_plus():
    """Test unary plus."""
    response = client.post(
        "/calculate",
        json={"expression": "+5"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 5.0
    assert data["error"] is None


def test_calculate_division_by_zero():
    """Test division by zero error handling."""
    response = client.post(
        "/calculate",
        json={"expression": "10 / 0"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is None
    assert "Division by zero" in data["error"]


def test_calculate_floor_division_by_zero():
    """Test floor division by zero error handling."""
    response = client.post(
        "/calculate",
        json={"expression": "10 // 0"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is None
    assert "Division by zero" in data["error"]


def test_calculate_modulo_by_zero():
    """Test modulo by zero error handling."""
    response = client.post(
        "/calculate",
        json={"expression": "10 % 0"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is None
    assert "Division by zero" in data["error"]


def test_calculate_invalid_expression():
    """Test invalid expression error handling."""
    response = client.post(
        "/calculate",
        json={"expression": "2 +"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is None
    assert "Invalid expression" in data["error"]


def test_calculate_malformed_input():
    """Test malformed input error handling."""
    response = client.post(
        "/calculate",
        json={"expression": "hello world"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is None
    assert "Invalid expression" in data["error"]


def test_calculate_empty_expression():
    """Test empty expression error handling."""
    response = client.post(
        "/calculate",
        json={"expression": ""}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is None
    assert "Invalid expression" in data["error"]


def test_calculate_whitespace_only():
    """Test whitespace-only expression."""
    response = client.post(
        "/calculate",
        json={"expression": "   "}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] is None
    assert "Invalid expression" in data["error"]


def test_calculate_single_number():
    """Test single number expression."""
    response = client.post(
        "/calculate",
        json={"expression": "42"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 42.0
    assert data["error"] is None


def test_calculate_decimal_numbers():
    """Test decimal number calculations."""
    response = client.post(
        "/calculate",
        json={"expression": "3.5 + 2.5"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 6.0
    assert data["error"] is None


def test_calculate_with_whitespace():
    """Test expression with whitespace is handled correctly."""
    response = client.post(
        "/calculate",
        json={"expression": "  2  +  3  "}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 5.0
    assert data["error"] is None

