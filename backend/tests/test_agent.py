import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_chat_calculator_intent():
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
    response = client.post(
        "/chat",
        json={
            "history": []
        }
    )
    
    # Should return 422 (validation error)
    assert response.status_code == 422


def test_chat_response_structure():
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
    assert "memory" in data
    if "tool_calls" in data and data["tool_calls"] is not None:
        assert isinstance(data["tool_calls"], list)
    memory = data["memory"]
    assert "slots" in memory
    assert "context_keys" in memory
    assert "history_length" in memory


def test_chat_multi_turn_conversation():
    response1 = client.post("/chat", json={"message": "Hello", "history": []})
    assert response1.status_code == 200
    data1 = response1.json()
    history = [
        {"role": "user", "content": "Hello", "timestamp": None},
        {"role": "assistant", "content": data1["response"], "timestamp": None}
    ]
    response2 = client.post("/chat", json={"message": "What can you do?", "history": history})
    assert response2.status_code == 200
    assert "response" in response2.json()


def test_chat_clarification_request():
    response = client.post("/chat", json={"message": "calculate", "history": []})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0


def test_chat_tool_calls_present():
    response = client.post("/chat", json={"message": "2 + 2", "history": []})
    assert response.status_code == 200
    data = response.json()
    if data.get("intent") == "calculator" and "tool_calls" in data and data["tool_calls"]:
        assert isinstance(data["tool_calls"], list)
        assert len(data["tool_calls"]) > 0
        tool_call = data["tool_calls"][0]
        assert "tool" in tool_call
        assert "input" in tool_call
        assert "output" in tool_call


def test_sequential_conversation_example_flow():
    """Test Part 1 example flow: Petaling Jaya -> Which outlet -> SS 2 opening time"""
    # Turn 1: "Is there an outlet in Petaling Jaya?"
    response1 = client.post("/chat", json={
        "message": "Is there an outlet in Petaling Jaya?",
        "history": []
    })
    assert response1.status_code == 200
    data1 = response1.json()
    assert "response" in data1
    assert "memory" in data1
    assert data1["intent"] in ["outlet_query", "general_chat"]
    
    # Check that memory tracks context
    memory1 = data1["memory"]
    assert "context_keys" in memory1
    
    # Turn 2: "SS 2, what's the opening time?"
    history = [
        {"role": "user", "content": "Is there an outlet in Petaling Jaya?", "timestamp": None},
        {"role": "assistant", "content": data1["response"], "timestamp": None}
    ]
    response2 = client.post("/chat", json={
        "message": "SS 2, what's the opening time?",
        "history": history
    })
    assert response2.status_code == 200
    data2 = response2.json()
    assert "response" in data2
    assert "memory" in data2
    
    # Verify memory persists across turns
    memory2 = data2["memory"]
    assert "context_keys" in memory2
    assert memory2["history_length"] >= 2

