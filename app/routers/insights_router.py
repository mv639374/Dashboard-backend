from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List
from app.services.insights_service import (
    calculate_overview_metrics,
    generate_performance_quadrants,
    analyze_competitor_threats,
    categorize_by_priority,
    analyze_no_rank_products,
    extract_citation_sources,
    generate_category_heatmap,
    identify_quick_wins,
    identify_battlegrounds,
    get_competitor_details,
    get_category_battle_details
)
from app.models.insights_schemas import (
    OverviewMetrics,
    PerformanceQuadrant,
    CompetitorThreat,
    PriorityCategory,
    NoRankAnalysis,
    CitationSource,
    CategoryHeatmapRow,
    QuickWin,
    BattlegroundCategory,
    CompetitorDetail,
    CategoryBattle
)
from app.core.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/overview", response_model=OverviewMetrics)
async def get_overview():
    """
    Get executive dashboard overview metrics
    
    Returns:
        OverviewMetrics with visibility score, market leadership, avg ranking, etc.
    """
    try:
        logger.info("📊 API: Fetching overview metrics...")
        metrics = calculate_overview_metrics()
        logger.info("✅ API: Successfully returned overview metrics")
        return metrics
    except Exception as e:
        logger.error(f"❌ API: Error fetching overview - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance-quadrants", response_model=List[PerformanceQuadrant])
async def get_performance_quadrants():
    """
    Get 2x2 performance quadrant matrix data
    
    Returns:
        List of categories with quadrant classification (Stars, Question Marks, Cash Cows, Dogs)
    """
    try:
        logger.info("📊 API: Fetching performance quadrants...")
        quadrants = generate_performance_quadrants()
        logger.info(f"✅ API: Successfully returned {len(quadrants)} quadrant data points")
        return quadrants
    except Exception as e:
        logger.error(f"❌ API: Error fetching quadrants - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competitor-analysis", response_model=List[CompetitorThreat])
async def get_competitor_analysis():
    """
    Get competitor threat analysis
    
    Returns:
        List of competitors with dominance metrics and threat levels
    """
    try:
        logger.info("📊 API: Fetching competitor analysis...")
        threats = analyze_competitor_threats()
        logger.info(f"✅ API: Successfully returned {len(threats)} competitor threats")
        return threats
    except Exception as e:
        logger.error(f"❌ API: Error fetching competitor analysis - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/priority-categories")
async def get_priority_categories():
    """
    Get categories categorized by severity (Critical/Medium/Low)
    
    Returns:
        Dictionary with three lists: critical, medium, low priority categories
    """
    try:
        logger.info("📊 API: Fetching priority categories...")
        categories = categorize_by_priority()
        logger.info(f"✅ API: Successfully returned priority categories")
        return categories
    except Exception as e:
        logger.error(f"❌ API: Error fetching priority categories - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/priority-categories/{severity}", response_model=List[PriorityCategory])
async def get_priority_categories_by_severity(severity: str):
    """
    Get categories by specific severity level
    
    Args:
        severity: "critical", "medium", or "low"
    
    Returns:
        List of categories with that severity level
    """
    try:
        severity_lower = severity.lower()
        if severity_lower not in ['critical', 'medium', 'low']:
            raise HTTPException(status_code=400, detail="Severity must be 'critical', 'medium', or 'low'")
        
        logger.info(f"📊 API: Fetching {severity_lower} priority categories...")
        all_categories = categorize_by_priority()
        categories = all_categories.get(severity_lower, [])
        logger.info(f"✅ API: Successfully returned {len(categories)} {severity_lower} categories")
        return categories
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ API: Error fetching {severity} categories - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/no-rank-analysis", response_model=NoRankAnalysis)
async def get_no_rank_analysis():
    """
    Get analysis of products where Amazon has no presence
    
    Returns:
        NoRankAnalysis with total missing products, top opportunity categories, etc.
    """
    try:
        logger.info("📊 API: Fetching no-rank analysis...")
        analysis = analyze_no_rank_products()
        logger.info("✅ API: Successfully returned no-rank analysis")
        return analysis
    except Exception as e:
        logger.error(f"❌ API: Error fetching no-rank analysis - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/citation-sources", response_model=List[CitationSource])
async def get_citation_sources(top_n: int = Query(50, ge=1, le=100)):
    """
    Get top citation sources from ChatGPT responses
    
    Args:
        top_n: Number of top sources to return (default: 50, max: 100)
    
    Returns:
        List of citation sources with frequency and impact scores
    """
    try:
        logger.info(f"📊 API: Fetching top {top_n} citation sources...")
        sources = extract_citation_sources()
        logger.info(f"✅ API: Successfully returned {len(sources[:top_n])} citation sources")
        return sources[:top_n]
    except Exception as e:
        logger.error(f"❌ API: Error fetching citation sources - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category-heatmap", response_model=List[CategoryHeatmapRow])
async def get_category_heatmap():
    """
    Get category performance heatmap data
    
    Returns:
        List of all categories with Amazon rank, score, gap, and status color
    """
    try:
        logger.info("📊 API: Fetching category heatmap...")
        heatmap = generate_category_heatmap()
        logger.info(f"✅ API: Successfully returned heatmap for {len(heatmap)} categories")
        return heatmap
    except Exception as e:
        logger.error(f"❌ API: Error fetching category heatmap - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick-wins", response_model=List[QuickWin])
async def get_quick_wins():
    """
    Get quick win opportunities (low-hanging fruit with <15% gap)
    
    Returns:
        List of categories with small gaps that can be easily improved
    """
    try:
        logger.info("📊 API: Fetching quick wins...")
        wins = identify_quick_wins()
        logger.info(f"✅ API: Successfully returned {len(wins)} quick wins")
        return wins
    except Exception as e:
        logger.error(f"❌ API: Error fetching quick wins - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/battlegrounds", response_model=List[BattlegroundCategory])
async def get_battlegrounds():
    """
    Get strategic battleground categories (medium gaps with high potential)
    
    Returns:
        List of categories worth strategic investment
    """
    try:
        logger.info("📊 API: Fetching battleground categories...")
        battlegrounds = identify_battlegrounds()
        logger.info(f"✅ API: Successfully returned {len(battlegrounds)} battlegrounds")
        return battlegrounds
    except Exception as e:
        logger.error(f"❌ API: Error fetching battlegrounds - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competitor/{competitor_name}", response_model=CompetitorDetail)
async def get_competitor_detail(competitor_name: str):
    """
    Get detailed analysis for a specific competitor
    
    Args:
        competitor_name: Name of the competitor
    
    Returns:
        CompetitorDetail with all categories, gaps, and strength areas
    """
    try:
        logger.info(f"📊 API: Fetching details for competitor '{competitor_name}'...")
        details = get_competitor_details(competitor_name)
        logger.info(f"✅ API: Successfully returned details for '{competitor_name}'")
        return details
    except Exception as e:
        logger.error(f"❌ API: Error fetching competitor details - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category-battle/{category_name}", response_model=CategoryBattle)
async def get_category_battle(category_name: str):
    """
    Get detailed battle analysis for a specific category
    
    Args:
        category_name: Name of the category
    
    Returns:
        CategoryBattle with top 5 competitors, product counts, and missing products
    """
    try:
        logger.info(f"📊 API: Fetching battle details for category '{category_name}'...")
        battle = get_category_battle_details(category_name)
        logger.info(f"✅ API: Successfully returned battle details for '{category_name}'")
        return battle
    except Exception as e:
        logger.error(f"❌ API: Error fetching category battle - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-insights")
async def get_all_insights():
    """
    Get all insights data in one call (for preloading)
    
    Returns:
        Dictionary with all insights data
    """
    try:
        logger.info("📊 API: Fetching all insights data...")
        
        data = {
            'overview': calculate_overview_metrics(),
            'performance_quadrants': generate_performance_quadrants(),
            'competitor_analysis': analyze_competitor_threats(),
            'priority_categories': categorize_by_priority(),
            'no_rank_analysis': analyze_no_rank_products(),
            'citation_sources': extract_citation_sources()[:50],
            'category_heatmap': generate_category_heatmap(),
            'quick_wins': identify_quick_wins(),
            'battlegrounds': identify_battlegrounds()
        }
        
        logger.info("✅ API: Successfully returned all insights data")
        return data
    except Exception as e:
        logger.error(f"❌ API: Error fetching all insights - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
