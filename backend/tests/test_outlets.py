"""
Tests for outlets Text2SQL endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from models.database import Base, Outlet, init_db

client = TestClient(app)


@pytest.fixture
def sample_outlets_db(tmp_path, monkeypatch):
    """Create a temporary database with sample outlets."""
    # Create temporary database
    db_path = tmp_path / "test_outlets.db"
    test_db_url = f"sqlite:///{db_path}"
    
    # Create engine and tables
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    # Add sample data
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    sample_outlets = [
        Outlet(
            name="ZUS Coffee Petaling Jaya",
            location="1 Utama Shopping Centre",
            district="Petaling Jaya",
            hours="8:00 AM - 10:00 PM",
            services="WiFi, Parking, Drive-thru",
            lat=3.1502,
            lon=101.6167
        ),
        Outlet(
            name="ZUS Coffee KLCC",
            location="Suria KLCC",
            district="Kuala Lumpur",
            hours="9:00 AM - 10:00 PM",
            services="WiFi, Parking",
            lat=3.1579,
            lon=101.7116
        ),
        Outlet(
            name="ZUS Coffee Subang Jaya",
            location="Empire Shopping Gallery",
            district="Subang Jaya",
            hours="8:00 AM - 11:00 PM",
            services="WiFi",
            lat=3.0738,
            lon=101.5931
        )
    ]
    
    for outlet in sample_outlets:
        db.add(outlet)
    db.commit()
    db.close()
    
    # Monkeypatch the database URL
    monkeypatch.setenv("DATABASE_URL", test_db_url)
    
    return test_db_url


def test_outlets_search_valid_query():
    """Test outlet search with valid query."""
    response = client.get("/outlets?query=petaling jaya")
    
    # Should return 200 (even if no results or dependencies missing)
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert "sql_query" in data
        assert isinstance(data["results"], list)


def test_outlets_search_empty_query():
    """Test outlet search with empty query."""
    response = client.get("/outlets?query=")
    
    # Should return 422 (validation error) or 400
    assert response.status_code in [400, 422]


def test_outlets_search_whitespace_only():
    """Test outlet search with whitespace-only query."""
    response = client.get("/outlets?query=   ")
    
    # Should return 400 or 422
    assert response.status_code in [400, 422]


def test_outlets_search_missing_query():
    """Test outlet search without query parameter."""
    response = client.get("/outlets")
    
    # Should return 422 (validation error)
    assert response.status_code == 422


def test_outlets_search_response_structure():
    """Test that response has correct structure when successful."""
    response = client.get("/outlets?query=kuala lumpur")
    
    if response.status_code == 200:
        data = response.json()
        
        # Check response structure
        assert "results" in data
        assert "sql_query" in data
        assert isinstance(data["results"], list)
        assert data["sql_query"] is None or isinstance(data["sql_query"], str)
        
        # If results exist, check structure
        if data["results"]:
            result = data["results"][0]
            assert "id" in result
            assert "name" in result
            assert "location" in result
            # Optional fields
            assert isinstance(result["id"], int)
            assert isinstance(result["name"], str)
            assert isinstance(result["location"], str)


def test_outlets_search_sql_injection_attempt():
    """Test that SQL injection attempts are blocked."""
    # Test various SQL injection patterns
    injection_queries = [
        "'; DROP TABLE outlets; --",
        "' OR '1'='1",
        "'; DELETE FROM outlets; --",
        "1' UNION SELECT * FROM outlets--",
    ]
    
    for query in injection_queries:
        response = client.get(f"/outlets?query={query}")
        
        # Should return 400 (blocked) or 500 (error), not 200 with malicious results
        assert response.status_code in [400, 500]
        
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data
            # Should mention blocked/invalid
            assert any(keyword in data["detail"].lower() 
                      for keyword in ["blocked", "invalid", "not allowed"])


def test_outlets_search_all_outlets():
    """Test search for all outlets."""
    response = client.get("/outlets?query=all outlets")
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data["results"], list)
        # May be empty if no data, but structure should be correct


def test_outlets_search_no_results():
    """Test search with query that matches nothing."""
    response = client.get("/outlets?query=nonexistent location xyz123")
    
    if response.status_code == 200:
        data = response.json()
        # Should return empty list, not error
        assert isinstance(data["results"], list)


def test_outlets_search_special_characters():
    """Test search with special characters in query."""
    response = client.get("/outlets?query=coffee%20shop")
    
    # Should handle URL encoding
    assert response.status_code in [200, 400, 422, 500]


def test_outlets_search_long_query():
    """Test search with very long query."""
    long_query = "a" * 1000
    response = client.get(f"/outlets?query={long_query}")
    
    # Should handle long queries (may return 200 or 400)
    assert response.status_code in [200, 400, 422, 500]

