"""
Products router for RAG-based product search.
"""
import logging
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from models.schemas import ProductsRequest, ProductsResponse, ProductResult
from services.rag_service import get_rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductsResponse)
async def search_products(
    query: str = Query(..., min_length=1, description="Search query for products"),
    top_k: Optional[int] = Query(default=None, description="Number of results to return")
) -> ProductsResponse:
    """
    Search for products using RAG (Retrieval Augmented Generation).
    
    Uses semantic search with FAISS vector store to find relevant products
    based on the query. Returns top results with optional LLM summary.
    
    Args:
        query: Search query string (e.g., "tumbler", "coffee mug")
        top_k: Number of results to return (default: 10 for category searches, 5 for specific searches)
        
    Returns:
        ProductsResponse with list of matching products and optional summary
        
    Raises:
        HTTPException: If query is empty or invalid
    """
    try:
        # Validate query
        query = query.strip()
        if not query:
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        logger.info(f"Searching products with query: {query}")
        
        # Ensure top_k is an integer (convert from Query object if needed)
        if top_k is not None:
            try:
                top_k = int(top_k)
            except (ValueError, TypeError):
                top_k = None
        
        # Determine top_k based on query type
        if top_k is None:
            query_lower = query.lower().strip()
            # Handle "all products" or "show all" - return all products
            if query_lower in ['all products', 'all', 'show all', 'list all', 'products']:
                top_k = 50  # Return all products
            # Category searches (plural forms, generic terms) should return more results
            elif any(keyword in query_lower for keyword in ['tumbler', 'tumblers', 'mug', 'mugs', 'cup', 'cups', 
                                                           'accessories', 'collectibles']):
                top_k = 20  # Return more results for category searches
            else:
                top_k = 10  # Default for specific product searches
        
        # Ensure top_k is an integer before passing to RAG service
        top_k = int(top_k)
        
        # Get RAG service and search
        rag_service = get_rag_service()
        results = rag_service.search(query, top_k=top_k)
        
        if not results:
            query_lower = query.lower().strip()
            category_map = {
                'tumbler': 'Tumbler', 'tumblers': 'Tumbler', 'cup': 'Tumbler', 'cups': 'Tumbler',
                'mug': 'Mugs', 'mugs': 'Mugs',
                'accessories': 'Accessories', 'collectibles': 'Collectibles'
            }
            
            category = next((cat for kw, cat in category_map.items() if kw in query_lower), None)
            if category:
                import json
                from pathlib import Path
                products_path = Path("data/products/products.json")
                if not products_path.exists():
                    products_path = Path(__file__).parent.parent / "data" / "products" / "products.json"
                if products_path.exists():
                    with open(products_path, 'r', encoding='utf-8') as f:
                        all_products = json.load(f)
                    category_products = [p for p in all_products if p.get('category') == category][:top_k]
                    results = [{"name": p.get("name", ""), "description": p.get("description", ""), 
                               "price": p.get("price"), "url": p.get("url"), "score": 1.0} 
                              for p in category_products]
        
        # Convert to ProductResult models
        product_results = [
            ProductResult(
                name=result.get("name", ""),
                description=result.get("description", ""),
                price=result.get("price"),
                url=result.get("url")
            )
            for result in results
        ]
        
        # Generate summary if we have results
        summary = None
        if product_results:
            # Simple summary (can be enhanced with LLM later)
            product_names = [p.name for p in product_results]
            summary = f"Found {len(product_results)} product(s): {', '.join(product_names)}"
        
        logger.info(f"Returning {len(product_results)} products")
        
        return ProductsResponse(
            results=product_results,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching products: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching products"
        )


@router.post("/rebuild-index")
async def rebuild_index() -> dict:
    """
    Rebuild the FAISS index from product data.
    
    This endpoint can be called after updating product data to refresh
    the vector store.
    
    Returns:
        Status message
    """
    try:
        logger.info("Rebuilding product index")
        rag_service = get_rag_service()
        rag_service.rebuild_index()
        return {
            "status": "success",
            "message": "Index rebuilt successfully"
        }
    except Exception as e:
        logger.error(f"Error rebuilding index: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while rebuilding the index"
        )

