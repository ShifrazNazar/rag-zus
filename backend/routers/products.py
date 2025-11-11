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
    query: str = Query(..., min_length=1, description="Search query for products")
) -> ProductsResponse:
    """
    Search for products using RAG (Retrieval Augmented Generation).
    
    Uses semantic search with FAISS vector store to find relevant products
    based on the query. Returns top-3 results with optional LLM summary.
    
    Args:
        query: Search query string (e.g., "tumbler", "coffee mug")
        
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
        
        # Get RAG service and search
        rag_service = get_rag_service()
        results = rag_service.search(query, top_k=3)
        
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

