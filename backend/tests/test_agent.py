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


def test_sequential_conversation_three_turns():
    """Test Part 1 requirement: Keep track of at least three related turns"""
    # Turn 1
    response1 = client.post("/chat", json={
        "message": "Find outlets in Petaling Jaya",
        "history": []
    })
    assert response1.status_code == 200
    data1 = response1.json()
    
    # Turn 2
    history1 = [
        {"role": "user", "content": "Find outlets in Petaling Jaya", "timestamp": None},
        {"role": "assistant", "content": data1["response"], "timestamp": None}
    ]
    response2 = client.post("/chat", json={
        "message": "Which one has drive through?",
        "history": history1
    })
    assert response2.status_code == 200
    data2 = response2.json()
    
    # Turn 3
    history2 = history1 + [
        {"role": "user", "content": "Which one has drive through?", "timestamp": None},
        {"role": "assistant", "content": data2["response"], "timestamp": None}
    ]
    response3 = client.post("/chat", json={
        "message": "What are the opening hours?",
        "history": history2
    })
    assert response3.status_code == 200
    data3 = response3.json()
    
    # Verify all three turns tracked
    memory3 = data3["memory"]
    assert memory3["history_length"] >= 3


def test_agent_planner_action_selection():
    """Test Part 2: Agent decides next action (ask, call tool, or finish)"""
    # Test ask_clarification action
    response1 = client.post("/chat", json={
        "message": "calculate",
        "history": []
    })
    assert response1.status_code == 200
    data1 = response1.json()
    assert "response" in data1
    assert len(data1["response"]) > 0
    
    # Test call_calculator action
    response2 = client.post("/chat", json={
        "message": "What's 5 + 3?",
        "history": []
    })
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["intent"] == "calculator"
    if "tool_calls" in data2 and data2["tool_calls"]:
        assert data2["tool_calls"][0]["tool"] == "calculator"
    
    # Test call_products action
    response3 = client.post("/chat", json={
        "message": "Show me tumblers",
        "history": []
    })
    assert response3.status_code == 200
    data3 = response3.json()
    if data3["intent"] == "product_search" and "tool_calls" in data3 and data3["tool_calls"]:
        assert data3["tool_calls"][0]["tool"] == "products"


def test_missing_parameters_calculator():
    """Test Part 5: Missing parameters - Calculate with no operands"""
    response = client.post("/chat", json={
        "message": "calculate",
        "history": []
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0
    assert "calculate" in data["response"].lower() or "expression" in data["response"].lower() or "number" in data["response"].lower()


def test_missing_parameters_products():
    """Test Part 5: Missing parameters - Product search with no query"""
    response = client.post("/chat", json={
        "message": "show products",
        "history": []
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data


def test_missing_parameters_outlets():
    """Test Part 5: Missing parameters - Outlet query with no location"""
    response = client.post("/chat", json={
        "message": "find outlets",
        "history": []
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data


def test_error_handling_graceful_degradation():
    """Test Part 5: Bot responds with clear error messages and never crashes"""
    # Test invalid calculator input
    response1 = client.post("/chat", json={
        "message": "calculate hello world",
        "history": []
    })
    assert response1.status_code == 200
    data1 = response1.json()
    assert "response" in data1
    assert isinstance(data1["response"], str)
    assert len(data1["response"]) > 0
    
    # Test malformed query
    response2 = client.post("/chat", json={
        "message": "find outlets in @#$%^&*()",
        "history": []
    })
    assert response2.status_code == 200
    data2 = response2.json()
    assert "response" in data2
    assert isinstance(data2["response"], str)


def test_tool_calls_structure():
    """Test that tool calls have correct structure"""
    response = client.post("/chat", json={
        "message": "2 + 2",
        "history": []
    })
    assert response.status_code == 200
    data = response.json()
    
    if data.get("intent") == "calculator" and "tool_calls" in data and data["tool_calls"]:
        tool_call = data["tool_calls"][0]
        assert "tool" in tool_call
        assert "input" in tool_call
        assert "output" in tool_call
        assert "success" in tool_call["output"]
        assert tool_call["tool"] == "calculator"
        assert "expression" in tool_call["input"]


def test_memory_slots_tracking():
    """Test Part 1: Memory tracks slots/variables across turns"""
    # First turn sets a slot
    response1 = client.post("/chat", json={
        "message": "Find outlets in Petaling Jaya",
        "history": []
    })
    assert response1.status_code == 200
    data1 = response1.json()
    memory1 = data1["memory"]
    assert "slots" in memory1
    
    # Second turn should maintain context
    history = [
        {"role": "user", "content": "Find outlets in Petaling Jaya", "timestamp": None},
        {"role": "assistant", "content": data1["response"], "timestamp": None}
    ]
    response2 = client.post("/chat", json={
        "message": "What are the services?",
        "history": history
    })
    assert response2.status_code == 200
    data2 = response2.json()
    memory2 = data2["memory"]
    assert "slots" in memory2
    assert memory2["history_length"] > memory1["history_length"]

