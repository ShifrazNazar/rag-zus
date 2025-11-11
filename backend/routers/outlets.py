"""
Outlets router for Text2SQL-based outlet search.
"""
import logging
from fastapi import APIRouter, Query, HTTPException

from models.schemas import OutletsRequest, OutletsResponse, OutletResult
from services.text2sql_service import get_text2sql_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/outlets", tags=["outlets"])


@router.get("", response_model=OutletsResponse)
async def search_outlets(
    query: str = Query(..., min_length=1, description="Natural language query for outlets")
) -> OutletsResponse:
    """
    Search for outlets using Text2SQL (Natural Language to SQL conversion).
    
    Converts natural language queries to SQL and executes them against
    the outlets database. Returns matching outlets with location details.
    
    Args:
        query: Natural language query (e.g., "outlets in petaling jaya")
        
    Returns:
        OutletsResponse with list of matching outlets and the SQL query used
        
    Raises:
        HTTPException: If query is empty, invalid, or contains SQL injection attempts
    """
    try:
        # Validate query
        query = query.strip()
        if not query:
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty"
            )
        
        logger.info(f"Searching outlets with query: {query}")
        
        # Get Text2SQL service and execute query
        text2sql_service = get_text2sql_service()
        results, sql_query = text2sql_service.query(query)
        
        # Convert to OutletResult models
        outlet_results = [
            OutletResult(
                id=result.get("id", 0),
                name=result.get("name", ""),
                location=result.get("location", ""),
                district=result.get("district"),
                hours=result.get("hours"),
                services=result.get("services"),
                lat=result.get("lat"),
                lon=result.get("lon")
            )
            for result in results
        ]
        
        logger.info(f"Returning {len(outlet_results)} outlets")
        
        return OutletsResponse(
            results=outlet_results,
            sql_query=sql_query
        )
        
    except ValueError as e:
        # SQL injection attempt or invalid query
        logger.warning(f"Invalid query detected: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid query: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching outlets: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching outlets"
        )

