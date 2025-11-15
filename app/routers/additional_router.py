from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.services.additional_service import (
    calculate_citation_visibility,
    calculate_source_authority_mapping,
    calculate_official_store_scores,
    calculate_trust_signals,
    calculate_product_availability_matrix,
    calculate_niche_opportunities,
    calculate_category_associations,
    calculate_competitor_specialties,
    calculate_intent_alignments,
    predict_rank_movement
)
from app.models.additional_schemas import (
    CitationVisibilityScore,
    SourceAuthorityMapping,
    OfficialStoreScore,
    TrustSignalHeatmap,
    ProductAvailabilityRow,
    NicheCategoryOpportunity,
    CategoryAssociationStrength,
    CompetitorSpecialty,
    IntentAlignment,
    RankPrediction,
    AllAdditionalData
)
from app.core.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/citation-visibility", response_model=CitationVisibilityScore)
async def get_citation_visibility():
    """
    Get citation frequency comparison across marketplaces
    
    Returns:
        CitationVisibilityScore with Amazon vs competitor mention counts
    """
    try:
        logger.info("📊 API: Fetching citation visibility...")
        data = calculate_citation_visibility()
        logger.info("✅ API: Successfully returned citation visibility")
        return data
    except Exception as e:
        logger.error(f"❌ API: Error fetching citation visibility - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/source-authority-map", response_model=SourceAuthorityMapping)
async def get_source_authority_map():
    """
    Get source to marketplace authority mapping
    
    Returns:
        SourceAuthorityMapping with nodes and links for Sankey diagram
    """
    try:
        logger.info("📊 API: Fetching source authority mapping...")
        data = calculate_source_authority_mapping()
        logger.info("✅ API: Successfully returned source authority mapping")
        return data
    except Exception as e:
        logger.error(f"❌ API: Error fetching source authority - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/official-store-scores", response_model=List[OfficialStoreScore])
async def get_official_store_scores():
    """
    Get official store recognition scores by category
    
    Returns:
        List of OfficialStoreScore with gap analysis
    """
    try:
        logger.info("📊 API: Fetching official store scores...")
        data = calculate_official_store_scores()
        logger.info(f"✅ API: Successfully returned {len(data)} official store scores")
        return data
    except Exception as e:
        logger.error(f"❌ API: Error fetching official store scores - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trust-signals", response_model=List[TrustSignalHeatmap])
async def get_trust_signals():
    """
    Get trust signal heatmap data
    
    Returns:
        List of TrustSignalHeatmap with positive/negative sentiment
    """
    try:
        logger.info("📊 API: Fetching trust signals...")
        data = calculate_trust_signals()
        logger.info(f"✅ API: Successfully returned {len(data)} trust signals")
        return data
    except Exception as e:
        logger.error(f"❌ API: Error fetching trust signals - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product-availability-matrix", response_model=List[ProductAvailabilityRow])
async def get_product_availability_matrix():
    """
    Get product availability matrix by category
    
    Returns:
        List of ProductAvailabilityRow with missing product analysis
    """
    try:
        logger.info("📊 API: Fetching product availability matrix...")
        data = calculate_product_availability_matrix()
        logger.info(f"✅ API: Successfully returned {len(data)} category availability data")
        return data
    except Exception as e:
        logger.error(f"❌ API: Error fetching product availability - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/niche-opportunities", response_model=List[NicheCategoryOpportunity])
async def get_niche_opportunities():
    """
    Get niche category opportunity analysis
    
    Returns:
        List of NicheCategoryOpportunity with radar chart metrics
    """
    try:
        logger.info("📊 API: Fetching niche opportunities...")
        data = calculate_niche_opportunities()
        logger.info(f"✅ API: Successfully returned {len(data)} niche opportunities")
        return data
    except Exception as e:
        logger.error(f"❌ API: Error fetching niche opportunities - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category-association", response_model=List[CategoryAssociationStrength])
async def get_category_association():
    """
    Get category association strength analysis
    
    Returns:
        List of CategoryAssociationStrength per marketplace
    """
    try:
        logger.info("📊 API: Fetching category associations...")
        data = calculate_category_associations()
        logger.info(f"✅ API: Successfully returned {len(data)} category associations")
        return data
    except Exception as e:
        logger.error(f"❌ API: Error fetching category associations - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competitor-specialty", response_model=List[CompetitorSpecialty])
async def get_competitor_specialty():
    """
    Get competitor specialty pattern analysis
    
    Returns:
        List of CompetitorSpecialty with dominated categories
    """
    try:
        logger.info("📊 API: Fetching competitor specialties...")
        data = calculate_competitor_specialties()
        logger.info(f"✅ API: Successfully returned {len(data)} competitor specialties")
        return data
    except Exception as e:
        logger.error(f"❌ API: Error fetching competitor specialties - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intent-alignment", response_model=List[IntentAlignment])
async def get_intent_alignment():
    """
    Get user intent to marketplace alignment
    
    Returns:
        List of IntentAlignment with win rates
    """
    try:
        logger.info("📊 API: Fetching intent alignments...")
        data = calculate_intent_alignments()
        logger.info(f"✅ API: Successfully returned {len(data)} intent alignments")
        return data
    except Exception as e:
        logger.error(f"❌ API: Error fetching intent alignments - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rank-prediction", response_model=RankPrediction)
async def get_rank_prediction(
    category: str = Query(..., description="Product category name"),
    products_to_add: int = Query(5, ge=0, le=50, description="Number of products to add"),
    citations_needed: int = Query(10, ge=0, le=100, description="Number of citation mentions needed")
):
    """
    Predict rank movement and ROI based on actions
    
    Args:
        category: Product category to analyze
        products_to_add: Number of products to add to catalog
        citations_needed: Number of citation mentions to target
    
    Returns:
        RankPrediction with timeline and ROI estimates
    """
    try:
        logger.info(f"📊 API: Predicting rank for {category}...")
        data = predict_rank_movement(category, products_to_add, citations_needed)
        logger.info("✅ API: Successfully returned rank prediction")
        return data
    except Exception as e:
        logger.error(f"❌ API: Error predicting rank - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-additional", response_model=AllAdditionalData)
async def get_all_additional():
    """
    Get all additional analytics data in one call (for preloading)
    
    Returns:
        AllAdditionalData with all analytics combined
    """
    try:
        logger.info("📊 API: Fetching all additional analytics...")
        
        data = AllAdditionalData(
            citation_visibility=calculate_citation_visibility(),
            source_authority=calculate_source_authority_mapping(),
            official_store_scores=calculate_official_store_scores(),
            trust_signals=calculate_trust_signals(),
            product_availability=calculate_product_availability_matrix(),
            niche_opportunities=calculate_niche_opportunities(),
            category_associations=calculate_category_associations(),
            competitor_specialties=calculate_competitor_specialties(),
            intent_alignments=calculate_intent_alignments()
        )
        
        logger.info("✅ API: Successfully returned all additional analytics")
        return data
    except Exception as e:
        logger.error(f"❌ API: Error fetching all additional analytics - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
