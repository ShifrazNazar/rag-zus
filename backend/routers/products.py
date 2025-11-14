import logging
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from models.schemas import ProductsResponse, ProductResult
from services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductsResponse)
async def search_products(
    query: str = Query(..., min_length=1, description="Search query for products"),
    top_k: Optional[int] = Query(default=None, description="Number of results to return")
) -> ProductsResponse:
    try:
        query = query.strip()
        if not query:
            query = "products"
        
        logger.info(f"Searching products with query: {query}")
        
        if top_k is not None:
            try:
                top_k = int(top_k)
            except (ValueError, TypeError):
                top_k = None
        
        if top_k is None:
            query_lower = query.lower().strip()
            if not query_lower or query_lower in ['all products', 'all', 'show all', 'list all', 'products', '/products']:
                top_k = 50
            elif any(specific in query_lower for specific in ['og cup', 'all day cup', 'all-can', 'frozee', 'og ceramic']):
                top_k = 5
            elif any(keyword in query_lower for keyword in ['tumbler', 'tumblers', 'mug', 'mugs', 'cup', 'cups', 
                                                           'accessories', 'collectibles']):
                top_k = 25
            else:
                top_k = 5
        
        top_k = int(top_k)
        
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
        
        product_results = [
            ProductResult(
                name=result.get("name", ""),
                description=result.get("description", ""),
                price=result.get("price"),
                url=result.get("url")
            )
            for result in results
        ]
        
        summary = None
        if product_results:
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
