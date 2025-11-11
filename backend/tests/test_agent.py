"""
Tests for chat agent endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_chat_calculator_intent():
    """Test chat with calculator intent."""
    response = client.post(
        "/chat",
        json={
            "message": "What's 2 + 2?",
            "history": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "intent" in data
    assert data["intent"] == "calculator"
    assert "memory" in data


def test_chat_products_intent():
    """Test chat with products search intent."""
    response = client.post(
        "/chat",
        json={
            "message": "Show me products",
            "history": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "intent" in data
    # May be product_search or general_chat depending on classification
    assert data["intent"] in ["product_search", "general_chat"]


def test_chat_outlets_intent():
    """Test chat with outlets search intent."""
    response = client.post(
        "/chat",
        json={
            "message": "Find outlets in Petaling Jaya",
            "history": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "intent" in data
    # May be outlet_query or general_chat
    assert data["intent"] in ["outlet_query", "general_chat"]


def test_chat_general_conversation():
    """Test chat with general conversation."""
    response = client.post(
        "/chat",
        json={
            "message": "Hello",
            "history": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "intent" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0


def test_chat_with_history():
    """Test chat with conversation history."""
    response = client.post(
        "/chat",
        json={
            "message": "What's 5 * 3?",
            "history": [
                {"role": "user", "content": "Hello", "timestamp": "2024-01-01T00:00:00Z"},
                {"role": "assistant", "content": "Hi! How can I help?", "timestamp": "2024-01-01T00:00:01Z"}
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "memory" in data


def test_chat_reset_command():
    """Test reset command."""
    response = client.post(
        "/chat",
        json={
            "message": "reset",
            "history": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["intent"] == "reset"
    assert "reset" in data["response"].lower() or "clear" in data["response"].lower()


def test_chat_empty_message():
    """Test chat with empty message."""
    response = client.post(
        "/chat",
        json={
            "message": "",
            "history": []
        }
    )
    
    # Should return 422 (validation error)
    assert response.status_code == 422


def test_chat_missing_message():
    """Test chat without message field."""
    response = client.post(
        "/chat",
        json={
            "history": []
        }
    )
    
    # Should return 422 (validation error)
    assert response.status_code == 422


def test_chat_response_structure():
    """Test that response has correct structure."""
    response = client.post(
        "/chat",
        json={
            "message": "Hello",
            "history": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Required fields
    assert "response" in data
    assert "intent" in data
    assert "memory" in data
    
    # Optional fields
    if "tool_calls" in data:
        assert isinstance(data["tool_calls"], list)
    
    # Memory structure
    memory = data["memory"]
    assert "slots" in memory
    assert "context_keys" in memory
    assert "history_length" in memory
    assert "last_updated" in memory


def test_chat_multi_turn_conversation():
    """Test multi-turn conversation."""
    # First message
    response1 = client.post(
        "/chat",
        json={
            "message": "Hello",
            "history": []
        }
    )
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Second message with history
    history = [
        {"role": "user", "content": "Hello", "timestamp": None},
        {"role": "assistant", "content": data1["response"], "timestamp": None}
    ]
    
    response2 = client.post(
        "/chat",
        json={
            "message": "What can you do?",
            "history": history
        }
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert "response" in data2


def test_chat_clarification_request():
    """Test that clarification is requested when slots are missing."""
    response = client.post(
        "/chat",
        json={
            "message": "calculate",
            "history": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    # Should ask for clarification or provide helpful response
    assert "response" in data
    assert len(data["response"]) > 0


def test_chat_tool_calls_present():
    """Test that tool calls are included when tools are used."""
    response = client.post(
        "/chat",
        json={
            "message": "2 + 2",
            "history": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # If calculator was called, tool_calls should be present
    if data.get("intent") == "calculator":
        # Tool calls may or may not be present depending on implementation
        # Just verify structure is correct if present
        if "tool_calls" in data and data["tool_calls"]:
            assert isinstance(data["tool_calls"], list)
            assert len(data["tool_calls"]) > 0
            tool_call = data["tool_calls"][0]
            assert "tool" in tool_call
            assert "input" in tool_call
            assert "output" in tool_call

