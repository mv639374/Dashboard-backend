from fastapi import APIRouter, HTTPException, Query
from typing import Dict
from app.services.analytics import (
    get_marketplace_rankings, 
    get_ranking_statistics,
    get_product_category_details
)
from app.core.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/ranking-table")
async def get_ranking_table(top_n: int = 5) -> Dict[str, Dict[str, int]]:
    """
    Get marketplace rankings table for all product categories
    
    Args:
        top_n: Number of top marketplaces to return per product (default: 5)
    
    Returns:
        Nested dictionary with marketplace rankings per product category
        {
            'Product Category': {'marketplace1': rank1, 'marketplace2': rank2, ...},
            ...
        }
    """
    try:
        logger.info(f"📊 API: Fetching ranking table (top {top_n})...")
        rankings = get_marketplace_rankings(top_n=top_n)
        logger.info(f"✅ API: Successfully returned rankings for {len(rankings)} products")
        return rankings
        
    except FileNotFoundError as e:
        logger.error(f"❌ API: File not found - {str(e)}")
        raise HTTPException(
            status_code=404,
            detail="Ranking data file not found. Please ensure the Excel file is in the correct location."
        )
    except ValueError as e:
        logger.error(f"❌ API: Invalid data - {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid data format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ API: Unexpected error - {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/product-category/{category}")
async def get_product_category_analytics(category: str) -> Dict:
    """
    Get detailed analytics for a specific product category
    
    Args:
        category: Name of the product category
    
    Returns:
        Dictionary containing:
        - category: Category name
        - products: List of unique product names in this category
        - marketplace_rankings: All marketplace rankings (not limited to top 5)
        - total_products: Number of unique products
        - total_marketplaces: Number of marketplaces
    """
    try:
        logger.info(f"📊 API: Fetching product category details for '{category}'...")
        details = get_product_category_details(category)
        logger.info(f"✅ API: Successfully returned details for '{category}'")
        return details
        
    except ValueError as e:
        logger.error(f"❌ API: Category not found - {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Product category not found: {category}"
        )
    except FileNotFoundError as e:
        logger.error(f"❌ API: File not found - {str(e)}")
        raise HTTPException(
            status_code=404,
            detail="Data file not found. Please ensure the Excel files are in the correct location."
        )
    except Exception as e:
        logger.error(f"❌ API: Unexpected error - {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/statistics")
async def get_statistics() -> Dict:
    """
    Get statistics about the ranking data
    
    Returns:
        Dictionary with statistics about products and marketplaces
    """
    try:
        logger.info("📊 API: Fetching statistics...")
        stats = get_ranking_statistics()
        logger.info("✅ API: Successfully returned statistics")
        return stats
        
    except Exception as e:
        logger.error(f"❌ API: Error fetching statistics - {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching statistics: {str(e)}"
        )
