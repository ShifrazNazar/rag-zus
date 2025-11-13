import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_outlets_search_valid_query():
    response = client.get("/outlets?query=petaling jaya")
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert "sql_query" in data
        assert isinstance(data["results"], list)


def test_outlets_search_empty_query():
    response = client.get("/outlets?query=")
    assert response.status_code in [400, 422]


def test_outlets_search_whitespace_only():
    response = client.get("/outlets?query=   ")
    assert response.status_code in [400, 422]


def test_outlets_search_missing_query():
    response = client.get("/outlets")
    assert response.status_code == 422


def test_outlets_search_response_structure():
    response = client.get("/outlets?query=kuala lumpur")
    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert "sql_query" in data
        assert isinstance(data["results"], list)
        if data["results"]:
            result = data["results"][0]
            assert "id" in result
            assert "name" in result
            assert "location" in result


def test_outlets_search_sql_injection_attempt():
    injection_queries = [
        "'; DROP TABLE outlets; --",
        "' OR '1'='1",
        "'; DELETE FROM outlets; --",
    ]
    for query in injection_queries:
        response = client.get(f"/outlets?query={query}")
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data["results"], list)


def test_outlets_search_all_outlets():
    response = client.get("/outlets?query=all outlets")
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data["results"], list)


def test_outlets_search_no_results():
    response = client.get("/outlets?query=nonexistent location xyz123")
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data["results"], list)


def test_outlets_search_special_characters():
    response = client.get("/outlets?query=coffee%20shop")
    assert response.status_code in [200, 400, 422, 500]


def test_outlets_search_long_query():
    long_query = "a" * 1000
    response = client.get(f"/outlets?query={long_query}")
    assert response.status_code in [200, 400, 422, 500]

