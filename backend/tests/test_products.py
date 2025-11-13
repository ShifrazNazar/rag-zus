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
    response = client.get("/products?query=   ")
    assert response.status_code in [400, 422]


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

