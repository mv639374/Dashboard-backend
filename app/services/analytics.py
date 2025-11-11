import pandas as pd
from pathlib import Path
from typing import Dict, List
from app.core.config import settings
from app.core.logger import setup_logger, log_excel_loading

logger = setup_logger(__name__)


def load_ranking_data() -> pd.DataFrame:
    """
    Load and validate the ranking data from Excel file 1
    
    Returns:
        pd.DataFrame: Loaded ranking data
    """
    try:
        file_path = settings.EXCEL_FILE_1
        
        if not file_path.exists():
            logger.error(f"Excel file not found: {file_path}")
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        # Load the Excel file
        df = pd.read_excel(file_path)
        
        # Log the loading information
        log_excel_loading(
            file_path=file_path,
            rows=len(df),
            columns=len(df.columns),
            sheet_name="Sheet1"
        )
        
        # Validate required columns
        required_columns = ['Product', 'source_normalized', 'rank']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        logger.info(f"✅ Successfully loaded {len(df)} rows with {df['Product'].nunique()} unique products")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading ranking data: {str(e)}")
        raise


def load_product_details_data() -> pd.DataFrame:
    """
    Load and validate the product details data from Excel file 2
    
    Returns:
        pd.DataFrame: Loaded product details data
    """
    try:
        file_path = settings.EXCEL_FILE_2
        
        if not file_path.exists():
            logger.error(f"Excel file not found: {file_path}")
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        # Load the Excel file
        df = pd.read_excel(file_path)
        
        # Log the loading information
        log_excel_loading(
            file_path=file_path,
            rows=len(df),
            columns=len(df.columns),
            sheet_name="Sheet1"
        )
        
        # Validate required columns
        required_columns = ['Product', 'product_name', 'source_normalized', 'rank']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        logger.info(f"✅ Successfully loaded {len(df)} rows with {df['Product'].nunique()} unique product categories")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading product details data: {str(e)}")
        raise


def get_marketplace_rankings(top_n: int = 5) -> Dict[str, Dict[str, int]]:
    """
    Get top N marketplace rankings for each product category
    
    Args:
        top_n: Number of top marketplaces to return per product (default: 5)
    
    Returns:
        Dict[str, Dict[str, int]]: Nested dictionary with structure:
        {
            'product_category_1': {'amazon': 1, 'flipkart': 2, ...},
            'product_category_2': {...},
            ...
        }
    """
    try:
        logger.info(f"🔄 Generating marketplace rankings (top {top_n})...")
        
        # Load the data
        df = load_ranking_data()
        
        # Filter for top N ranks
        df_top = df[df['rank'] <= top_n].copy()
        
        # Sort by product and rank
        df_top = df_top.sort_values(['Product', 'rank'])
        
        # Create the nested dictionary
        rankings = {}
        
        for product in df_top['Product'].unique():
            product_data = df_top[df_top['Product'] == product]
            
            # Create marketplace: rank mapping for this product
            marketplace_ranks = {}
            for _, row in product_data.iterrows():
                marketplace = row['source_normalized']
                rank = int(row['rank'])
                marketplace_ranks[marketplace] = rank
            
            rankings[product] = marketplace_ranks
        
        logger.info(f"✅ Generated rankings for {len(rankings)} product categories")
        logger.info(f"📊 Sample products: {list(rankings.keys())[:5]}")
        
        return rankings
        
    except Exception as e:
        logger.error(f"❌ Error generating marketplace rankings: {str(e)}")
        raise


def get_product_category_details(product_category: str) -> Dict:
    """
    Get detailed information for a specific product category including:
    - All unique products in this category
    - All marketplace rankings for this category (not limited to top 5)
    - Count of how many products each marketplace appears in
    
    Args:
        product_category: Name of the product category
    
    Returns:
        Dict with structure:
        {
            'category': str,
            'products': List[str],  # Unique product names
            'marketplace_rankings': Dict[str, int],  # All marketplaces with their ranks
            'marketplace_product_counts': Dict[str, int],  # Count of products each marketplace appears in
            'total_products': int,
            'total_marketplaces': int
        }
    """
    try:
        logger.info(f"🔄 Fetching details for category: {product_category}")
        
        # Load both datasets
        df_rankings = load_ranking_data()
        df_details = load_product_details_data()
        
        # Filter for the specific product category from rankings data
        category_rankings = df_rankings[df_rankings['Product'] == product_category].copy()
        
        if category_rankings.empty:
            logger.warning(f"⚠️ No ranking data found for category: {product_category}")
            raise ValueError(f"Product category not found: {product_category}")
        
        # Filter for the specific product category from details data
        category_details = df_details[df_details['Product'] == product_category].copy()
        
        # Get unique product names
        unique_products = sorted(category_details['product_name'].unique().tolist()) if not category_details.empty else []
        
        # Get all marketplace rankings (not limited to top 5)
        marketplace_rankings = {}
        category_rankings_sorted = category_rankings.sort_values('rank')
        
        for _, row in category_rankings_sorted.iterrows():
            marketplace = row['source_normalized']
            rank = int(row['rank'])
            marketplace_rankings[marketplace] = rank
        
        # Count how many products each marketplace appears in
        marketplace_product_counts = {}
        if not category_details.empty:
            # Group by marketplace and count unique products
            counts = category_details.groupby('source_normalized')['product_name'].nunique()
            marketplace_product_counts = counts.to_dict()
        
        result = {
            'category': product_category,
            'products': unique_products,
            'marketplace_rankings': marketplace_rankings,
            'marketplace_product_counts': marketplace_product_counts,
            'total_products': len(unique_products),
            'total_marketplaces': len(marketplace_rankings)
        }
        
        logger.info(f"✅ Retrieved {result['total_products']} products and {result['total_marketplaces']} marketplaces for {product_category}")
        logger.info(f"📊 Marketplace product counts: {marketplace_product_counts}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error fetching product category details: {str(e)}")
        raise


def get_ranking_statistics() -> Dict[str, any]:
    """
    Get statistics about the ranking data
    
    Returns:
        Dict with statistics
    """
    try:
        df = load_ranking_data()
        
        stats = {
            'total_products': int(df['Product'].nunique()),
            'total_marketplaces': int(df['source_normalized'].nunique()),
            'total_entries': int(len(df)),
            'products_list': sorted(df['Product'].unique().tolist()),
            'top_marketplaces': df[df['rank'] == 1]['source_normalized'].value_counts().head(10).to_dict()
        }
        
        logger.info(f"📊 Statistics generated: {stats['total_products']} products, {stats['total_marketplaces']} marketplaces")
        
        return stats
        
    except Exception as e:
        logger.error(f"Error generating statistics: {str(e)}")
        raise
