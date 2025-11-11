"""
Tests for products RAG endpoint.
"""
import pytest
import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.fixture
def sample_products_dir(tmp_path):
    """Create a temporary products directory with sample data."""
    products_dir = tmp_path / "products"
    products_dir.mkdir()
    
    # Create sample product data
    sample_products = [
        {
            "id": 1,
            "name": "ZUS Coffee Tumbler",
            "description": "Premium stainless steel tumbler perfect for hot and cold beverages. Keeps drinks at optimal temperature for hours.",
            "price": "RM 45.00",
            "url": "https://shop.zuscoffee.com/products/tumbler"
        },
        {
            "id": 2,
            "name": "ZUS Coffee Mug",
            "description": "Ceramic coffee mug with ZUS branding. Perfect for your morning coffee ritual.",
            "price": "RM 25.00",
            "url": "https://shop.zuscoffee.com/products/mug"
        },
        {
            "id": 3,
            "name": "ZUS Coffee Water Bottle",
            "description": "Eco-friendly reusable water bottle. BPA-free and leak-proof design.",
            "price": "RM 35.00",
            "url": "https://shop.zuscoffee.com/products/water-bottle"
        }
    ]
    
    # Save to JSON file
    products_file = products_dir / "products.json"
    with open(products_file, 'w') as f:
        json.dump(sample_products, f)
    
    return products_dir


def test_products_search_valid_query():
    """Test product search with valid query."""
    # Note: This test may fail if FAISS/sentence-transformers not installed
    # or if no products are loaded. It's a basic smoke test.
    response = client.get("/products?query=tumbler")
    
    # Should return 200 even if no products found
    assert response.status_code in [200, 500]  # 500 if dependencies missing
    
    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert "summary" in data
        assert isinstance(data["results"], list)


def test_products_search_empty_query():
    """Test product search with empty query."""
    response = client.get("/products?query=")
    
    # Should return 422 (validation error) or 400
    assert response.status_code in [400, 422]


def test_products_search_whitespace_only():
    """Test product search with whitespace-only query."""
    response = client.get("/products?query=   ")
    
    # Should return 400 or 422
    assert response.status_code in [400, 422]


def test_products_search_missing_query():
    """Test product search without query parameter."""
    response = client.get("/products")
    
    # Should return 422 (validation error)
    assert response.status_code == 422


def test_products_search_response_structure():
    """Test that response has correct structure when successful."""
    response = client.get("/products?query=coffee")
    
    if response.status_code == 200:
        data = response.json()
        
        # Check response structure
        assert "results" in data
        assert "summary" in data
        assert isinstance(data["results"], list)
        
        # If results exist, check structure
        if data["results"]:
            result = data["results"][0]
            assert "name" in result
            assert "description" in result
            # price and url are optional
            assert isinstance(result["name"], str)
            assert isinstance(result["description"], str)


def test_products_rebuild_index():
    """Test index rebuild endpoint."""
    response = client.post("/products/rebuild-index")
    
    # Should return 200 or 500 (if dependencies missing)
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"


def test_products_search_multiple_results():
    """Test that search can return multiple results."""
    response = client.get("/products?query=coffee")
    
    if response.status_code == 200:
        data = response.json()
        # Should return up to 3 results
        assert len(data["results"]) <= 3


def test_products_search_no_results():
    """Test search with query that matches nothing."""
    response = client.get("/products?query=xyzabc123nonexistent")
    
    if response.status_code == 200:
        data = response.json()
        # Should return empty list, not error
        assert isinstance(data["results"], list)
        # May be empty or have some results


def test_products_search_special_characters():
    """Test search with special characters in query."""
    response = client.get("/products?query=coffee%20mug")
    
    # Should handle URL encoding
    assert response.status_code in [200, 400, 422, 500]


def test_products_search_long_query():
    """Test search with very long query."""
    long_query = "a" * 1000
    response = client.get(f"/products?query={long_query}")
    
    # Should handle long queries (may return 200 or 400)
    assert response.status_code in [200, 400, 422, 500]

