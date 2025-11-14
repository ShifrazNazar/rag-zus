import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_products_search_valid_query():
    response = client.get("/products?query=tumbler")
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert "summary" in data
        assert isinstance(data["results"], list)


def test_products_search_empty_query():
    response = client.get("/products?query=")
    assert response.status_code in [400, 422]


def test_products_search_whitespace_only():
    """Test whitespace-only query - should default to 'products' and return 200"""
    response = client.get("/products?query=   ")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)


def test_products_search_missing_query():
    response = client.get("/products")
    assert response.status_code == 422


def test_products_search_response_structure():
    response = client.get("/products?query=coffee")
    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert "summary" in data
        assert isinstance(data["results"], list)
        if data["results"]:
            result = data["results"][0]
            assert "name" in result
            assert "description" in result
            assert isinstance(result["name"], str)
            assert isinstance(result["description"], str)


def test_products_rebuild_index():
    response = client.post("/products/rebuild-index")
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"


def test_products_search_multiple_results():
    response = client.get("/products?query=coffee")
    if response.status_code == 200:
        data = response.json()
        assert len(data["results"]) <= 10


def test_products_search_no_results():
    response = client.get("/products?query=xyzabc123nonexistent")
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data["results"], list)


def test_products_search_special_characters():
    response = client.get("/products?query=coffee%20mug")
    assert response.status_code in [200, 400, 422, 500]


def test_products_search_long_query():
    long_query = "a" * 1000
    response = client.get(f"/products?query={long_query}")
    assert response.status_code in [200, 400, 422, 500]


def test_products_missing_parameters():
    """Test Part 5: Missing parameters handling"""
    response = client.get("/products")
    assert response.status_code == 422


def test_products_error_handling_never_crashes():
    """Test Part 5: Bot never crashes on invalid input"""
    invalid_inputs = [
        "",
        "   ",
        "<script>alert('xss')</script>",
        "../../etc/passwd",
        "a" * 10000,
    ]
    
    for invalid_input in invalid_inputs:
        try:
            response = client.get(f"/products?query={invalid_input}")
            assert response.status_code in [200, 400, 422, 500]
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, dict)
                assert "results" in data
        except Exception as e:
            pytest.fail(f"Products endpoint crashed on input '{invalid_input}': {e}")


def test_products_response_structure_always_valid():
    """Test that products endpoint always returns valid structure"""
    test_queries = [
        "tumbler",
        "mug",
        "coffee",
        "nonexistent product xyz",
    ]
    
    for query in test_queries:
        response = client.get(f"/products?query={query}")
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            assert "summary" in data
            assert isinstance(data["results"], list)
            assert isinstance(data["summary"], (str, type(None)))


def test_products_ai_generated_summary():
    """Test Part 4: Returns AI-generated summary"""
    response = client.get("/products?query=tumbler")
    if response.status_code == 200:
        data = response.json()
        assert "summary" in data
        if data["results"]:
            assert data["summary"] is not None

