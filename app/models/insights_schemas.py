from pydantic import BaseModel
from typing import List, Dict, Optional


class OverviewMetrics(BaseModel):
    """Executive dashboard overview metrics"""
    visibility_score: float  # % of categories where Amazon appears
    market_leadership_score: float  # % of categories where Amazon is #1
    average_ranking: float  # Mean rank across all categories
    opportunity_gap: float  # % of categories where Amazon is not #1
    total_categories: int
    categories_rank_1: int
    categories_not_rank_1: int


class PerformanceQuadrant(BaseModel):
    """Performance quadrant data point"""
    category: str
    amazon_score: float
    category_size: int  # Number of products
    amazon_rank: int
    quadrant: str  # "Stars", "Question Marks", "Cash Cows", "Dogs"


class CompetitorThreat(BaseModel):
    """Competitor threat analysis"""
    competitor_name: str
    categories_dominated: int
    average_gap_percentage: float
    total_wins: int
    threat_level: str  # "Critical", "High", "Medium", "Low"
    dominated_categories: List[str]


class PriorityCategory(BaseModel):
    """Category with priority scoring"""
    category: str
    current_rank: int
    gap_percentage: float
    competitor: str
    competitor_score: float
    amazon_score: float
    severity: str  # "Critical", "Medium", "Low"
    priority_score: float


class NoRankProduct(BaseModel):
    """Product where Amazon has no presence"""
    product_category: str
    product_name: str
    citations: Optional[str] = None


class CategoryOpportunity(BaseModel):
    """Category opportunity with product count"""
    category: str
    product_count: int


class NoRankAnalysis(BaseModel):
    """No-rank analysis summary"""
    total_missing_products: int
    categories_affected: int
    top_opportunity_categories: List[CategoryOpportunity]
    products_with_citations: int
    sample_products: List[NoRankProduct]


class CitationSource(BaseModel):
    """Citation source intelligence"""
    domain: str
    frequency: int
    categories: List[str]
    impact_score: float


class CategoryHeatmapRow(BaseModel):
    """Single row in category heatmap"""
    category: str
    amazon_rank: int
    amazon_score: float
    gap_to_first: float
    competitor_name: str
    status_color: str  # "green", "yellow", "orange", "red"


class QuickWin(BaseModel):
    """Quick win opportunity"""
    category: str
    current_rank: int
    gap_percentage: float
    competitor: str
    action_items: List[str]
    estimated_effort: str  # "Low", "Medium", "High"


class BattlegroundCategory(BaseModel):
    """Strategic battleground category"""
    category: str
    amazon_rank: int
    gap_percentage: float
    competitor: str
    product_volume: str  # "High", "Medium", "Low"
    investment_priority: str  # "High", "Medium", "Low"


class CompetitorDetail(BaseModel):
    """Detailed competitor analysis"""
    competitor_name: str
    total_categories_dominated: int
    average_gap: float
    categories: List[Dict]  # [{category, rank, gap, amazon_rank}]
    strength_areas: List[str]


class CategoryBattle(BaseModel):
    """Detailed category battle analysis"""
    category: str
    amazon_rank: int
    amazon_score: float
    top_5_competitors: List[Dict]  # [{name, rank, score, gap}]
    product_count: int
    amazon_product_count: int
    missing_product_count: int
