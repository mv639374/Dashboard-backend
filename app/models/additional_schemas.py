from pydantic import BaseModel
from typing import List, Dict, Optional


class TopSource(BaseModel):
    """Top citation source"""
    source: str
    count: int


class CitationVisibilityScore(BaseModel):
    """Citation frequency comparison across marketplaces"""
    amazon_mentions: int
    competitor_mentions: int
    total_citations: int
    amazon_percentage: float
    competitor_percentage: float
    visibility_ratio: float  # Competitor/Amazon ratio
    top_sources: List[TopSource]  # List of top sources with counts
    source_breakdown: Dict[str, Dict[str, int]]  # {source: {marketplace: count}}



class SourceAuthorityNode(BaseModel):
    """Node for Sankey diagram"""
    source: str
    target: str
    value: int


class SourceAuthorityMapping(BaseModel):
    """Source to marketplace flow data"""
    nodes: List[str]  # All unique sources and marketplaces
    links: List[SourceAuthorityNode]  # Flow connections
    gateway_sources: List[Dict]  # Top sources that influence recommendations
    total_flows: int


class OfficialStoreScore(BaseModel):
    """Official store recognition by category"""
    category: str
    amazon_official_mentions: int
    competitor_official_mentions: int
    gap_score: float
    top_competitor: str
    recommendation: str


class TrustKeyword(BaseModel):
    """Trust signal keyword with count"""
    keyword: str
    count: int
    sentiment: str  # positive, negative, neutral


class TrustSignalHeatmap(BaseModel):
    """Trust signals by marketplace"""
    marketplace: str
    positive_signals: List[TrustKeyword]
    negative_signals: List[TrustKeyword]
    trust_score: float  # 0-100
    total_mentions: int


class ProductAvailabilityRow(BaseModel):
    """Product availability for a category"""
    category: str
    total_products: int
    amazon_available: int
    amazon_percentage: float
    competitor_availability: Dict[str, int]  # {marketplace: count}
    missing_products: List[str]
    revenue_opportunity: float  # Estimated monthly revenue


class NicheCategoryOpportunity(BaseModel):
    """Niche category opportunity metrics"""
    category: str
    citation_frequency: float  # 0-100
    amazon_current_rank: int
    competitor_strength: float  # 0-100
    product_count_gap: int
    revenue_potential: float  # 0-100
    opportunity_score: float  # Overall score
    quick_win: bool


class CategoryAssociationStrength(BaseModel):
    """Category association strength for a marketplace"""
    marketplace: str
    category: str
    win_rate: float  # % of times ranked #1
    top_3_rate: float  # % of times in top 3
    avg_score: float  # Average normalized score
    association_strength: float  # 0-100 calculated score
    perception_level: str  # Strong, Medium, Weak


class CompetitorSpecialty(BaseModel):
    """Competitor specialty pattern"""
    competitor_name: str
    dominated_categories: List[str]
    specialty_pattern: str  # e.g., "Imported/niche", "Indian mainstream"
    avg_gap_to_amazon: float
    total_wins: int
    action_recommendation: str


class IntentAlignment(BaseModel):
    """User intent to marketplace alignment"""
    intent: str  # e.g., "Cheapest price", "Fast delivery"
    amazon_win_rate: float
    top_competitor: str
    competitor_win_rate: float
    match_strength: str  # Strong, Medium, Weak
    recommendation: str


class ScenarioInput(BaseModel):
    """Input for scenario builder"""
    category: str
    products_to_add: int
    citation_sites_to_target: int
    investment_amount: float


class RankPrediction(BaseModel):
    """Rank movement prediction"""
    category: str
    current_rank: int
    predicted_rank: int
    gap_reduction: float
    citations_needed: int
    estimated_timeline_months: int
    revenue_impact_monthly: float
    investment_required: float
    roi_multiplier: float


class AllAdditionalData(BaseModel):
    """All additional analytics data"""
    citation_visibility: CitationVisibilityScore
    source_authority: SourceAuthorityMapping
    official_store_scores: List[OfficialStoreScore]
    trust_signals: List[TrustSignalHeatmap]
    product_availability: List[ProductAvailabilityRow]
    niche_opportunities: List[NicheCategoryOpportunity]
    category_associations: List[CategoryAssociationStrength]
    competitor_specialties: List[CompetitorSpecialty]
    intent_alignments: List[IntentAlignment]
