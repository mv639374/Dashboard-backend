import pandas as pd
import numpy as np
from typing import Dict, List
from collections import defaultdict, Counter
import re
from urllib.parse import urlparse

from app.core.config import settings
from app.core.logger import setup_logger
from app.services.analytics import load_ranking_data, load_product_details_data

logger = setup_logger(__name__)


def load_no_rank_data() -> pd.DataFrame:
    """Load products without Amazon with citations"""
    try:
        file_path = settings.EXCEL_FILE_3
        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        df = pd.read_excel(file_path)
        logger.info(f"✅ Loaded {len(df)} no-rank products with citations")
        return df
    except Exception as e:
        logger.error(f"Error loading no-rank data: {str(e)}")
        raise


def extract_domains_from_citations(citations_series: pd.Series) -> List[str]:
    """Extract domains from citation URLs"""
    domains = []
    for citation in citations_series.dropna():
        urls = re.findall(r'https?://([^\s/\]]+)', str(citation))
        domains.extend([url.replace('www.', '') for url in urls])
    return domains


def calculate_sentiment_score(text: str, positive_keywords: List[str], negative_keywords: List[str]) -> float:
    """Calculate sentiment score from text"""
    text_lower = text.lower()
    positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
    negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
    
    total = positive_count + negative_count
    if total == 0:
        return 50.0  # Neutral
    
    return (positive_count / total) * 100


def calculate_citation_visibility() -> Dict:
    """Calculate citation frequency index"""
    try:
        logger.info("🔄 Calculating citation visibility...")
        
        df_no_rank = load_no_rank_data()
        
        # Extract all domains
        all_domains = extract_domains_from_citations(df_no_rank['Citations'])
        domain_counts = Counter(all_domains)
        
        # Count Amazon mentions
        amazon_mentions = sum(count for domain, count in domain_counts.items() if 'amazon' in domain.lower())
        
        # Count competitor mentions (all non-Amazon)
        competitor_mentions = sum(count for domain, count in domain_counts.items() if 'amazon' not in domain.lower())
        
        total_citations = amazon_mentions + competitor_mentions
        
        # Top sources
        top_sources = [
            {'source': domain, 'count': count}
            for domain, count in domain_counts.most_common(20)
        ]
        
        # Source breakdown by marketplace (simplified - based on domain matching)
        source_breakdown = {}
        for domain, count in domain_counts.most_common(15):
            source_breakdown[domain] = {
                'amazon': count if 'amazon' in domain.lower() else 0,
                'competitors': count if 'amazon' not in domain.lower() else 0
            }
        
        result = {
            'amazon_mentions': amazon_mentions,
            'competitor_mentions': competitor_mentions,
            'total_citations': total_citations,
            'amazon_percentage': (amazon_mentions / total_citations * 100) if total_citations > 0 else 0,
            'competitor_percentage': (competitor_mentions / total_citations * 100) if total_citations > 0 else 0,
            'visibility_ratio': (competitor_mentions / amazon_mentions) if amazon_mentions > 0 else 0,
            'top_sources': top_sources,
            'source_breakdown': source_breakdown
        }
        
        logger.info(f"✅ Citation visibility: Amazon {amazon_mentions}, Competitors {competitor_mentions}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error calculating citation visibility: {str(e)}")
        raise


def calculate_source_authority_mapping() -> Dict:
    """Calculate source to marketplace flow"""
    try:
        logger.info("🔄 Calculating source authority mapping...")
        
        df_details = load_product_details_data()
        df_no_rank = load_no_rank_data()
        
        # Extract domains from citations
        all_domains = extract_domains_from_citations(df_no_rank['Citations'])
        domain_counts = Counter(all_domains)
        
        # Get marketplace counts from rankings
        marketplace_counts = df_details['source_normalized'].value_counts().to_dict()
        
        # Create nodes (sources + marketplaces)
        top_sources = [domain for domain, _ in domain_counts.most_common(10)]
        top_marketplaces = list(marketplace_counts.keys())[:10]
        nodes = top_sources + top_marketplaces
        
        # Create links (simplified - proportional distribution)
        links = []
        for source in top_sources:
            source_count = domain_counts[source]
            for marketplace, mp_count in list(marketplace_counts.items())[:5]:
                # Proportional flow based on marketplace popularity
                flow_value = int(source_count * (mp_count / sum(marketplace_counts.values())))
                if flow_value > 0:
                    links.append({
                        'source': source,
                        'target': marketplace,
                        'value': flow_value
                    })
        
        # Gateway sources (top influencers)
        gateway_sources = [
            {
                'source': domain,
                'total_citations': count,
                'influence_score': round(count / domain_counts.most_common(1)[0][1] * 100, 1)
            }
            for domain, count in domain_counts.most_common(10)
        ]
        
        result = {
            'nodes': nodes,
            'links': links,
            'gateway_sources': gateway_sources,
            'total_flows': len(links)
        }
        
        logger.info(f"✅ Source authority mapping: {len(nodes)} nodes, {len(links)} flows")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error calculating source authority: {str(e)}")
        raise


def calculate_official_store_scores() -> List[Dict]:
    """Calculate official store recognition"""
    try:
        logger.info("🔄 Calculating official store scores...")
        
        df_details = load_product_details_data()
        df_rankings = load_ranking_data()
        
        scores = []
        
        for category in df_rankings['Product'].unique()[:20]:  # Top 20 categories
            cat_details = df_details[df_details['Product'] == category]
            
            # Count "official" mentions in extra field
            amazon_official = 0
            competitor_official = 0
            top_competitor = None
            max_competitor_mentions = 0
            
            for _, row in cat_details.iterrows():
                extra_text = str(row.get('extra', '')).lower()
                is_amazon = 'amazon' in str(row['source_normalized']).lower()
                
                official_count = extra_text.count('official') + extra_text.count('authorized')
                
                if is_amazon:
                    amazon_official += official_count
                else:
                    competitor_official += official_count
                    if official_count > max_competitor_mentions:
                        max_competitor_mentions = official_count
                        top_competitor = row['source_normalized']
            
            gap_score = ((competitor_official - amazon_official) / max(competitor_official, 1)) * 100 if competitor_official > 0 else 0
            
            recommendation = "Establish official partnership" if gap_score > 30 else "Maintain current status"
            
            scores.append({
                'category': category,
                'amazon_official_mentions': amazon_official,
                'competitor_official_mentions': competitor_official,
                'gap_score': round(gap_score, 1),
                'top_competitor': top_competitor or 'N/A',
                'recommendation': recommendation
            })
        
        logger.info(f"✅ Calculated official store scores for {len(scores)} categories")
        return scores
        
    except Exception as e:
        logger.error(f"❌ Error calculating official store scores: {str(e)}")
        raise


def calculate_trust_signals() -> List[Dict]:
    """Calculate trust signal heatmap"""
    try:
        logger.info("🔄 Calculating trust signals...")
        
        df_details = load_product_details_data()
        
        positive_keywords = ['genuine', 'authentic', 'verified', 'trusted', 'excellent', 'fast delivery', 'quality']
        negative_keywords = ['fake', 'counterfeit', 'delayed', 'poor quality', 'scam', 'fraud']
        
        trust_signals = []
        
        # Group by marketplace
        for marketplace in df_details['source_normalized'].unique()[:15]:
            mp_data = df_details[df_details['source_normalized'] == marketplace]
            
            # Analyze extra field for trust keywords
            all_text = ' '.join(mp_data['extra'].astype(str).str.lower())
            
            positive_found = []
            for keyword in positive_keywords:
                count = all_text.count(keyword)
                if count > 0:
                    positive_found.append({'keyword': keyword, 'count': count, 'sentiment': 'positive'})
            
            negative_found = []
            for keyword in negative_keywords:
                count = all_text.count(keyword)
                if count > 0:
                    negative_found.append({'keyword': keyword, 'count': count, 'sentiment': 'negative'})
            
            total_positive = sum(item['count'] for item in positive_found)
            total_negative = sum(item['count'] for item in negative_found)
            total_mentions = total_positive + total_negative
            
            trust_score = (total_positive / total_mentions * 100) if total_mentions > 0 else 50.0
            
            trust_signals.append({
                'marketplace': marketplace,
                'positive_signals': positive_found[:5],
                'negative_signals': negative_found[:5],
                'trust_score': round(trust_score, 1),
                'total_mentions': total_mentions
            })
        
        # Sort by trust score
        trust_signals.sort(key=lambda x: -x['trust_score'])
        
        logger.info(f"✅ Calculated trust signals for {len(trust_signals)} marketplaces")
        return trust_signals
        
    except Exception as e:
        logger.error(f"❌ Error calculating trust signals: {str(e)}")
        raise


def calculate_product_availability_matrix() -> List[Dict]:
    """Calculate product availability by category"""
    try:
        logger.info("🔄 Calculating product availability matrix...")
        
        df_details = load_product_details_data()
        df_no_rank = load_no_rank_data()
        df_rankings = load_ranking_data()
        
        availability = []
        
        for category in df_rankings['Product'].unique()[:20]:
            cat_details = df_details[df_details['Product'] == category]
            cat_no_rank = df_no_rank[df_no_rank['Product Category'] == category]
            
            total_products = cat_details['product_name'].nunique() + len(cat_no_rank)
            amazon_available = cat_details[cat_details['source_normalized'].str.lower() == 'amazon']['product_name'].nunique()
            
            # Competitor availability
            competitor_avail = {}
            for mp in cat_details['source_normalized'].unique():
                if 'amazon' not in mp.lower():
                    count = cat_details[cat_details['source_normalized'] == mp]['product_name'].nunique()
                    competitor_avail[mp] = count
            
            missing_products = cat_no_rank['Product Name'].tolist()[:10]  # Top 10
            
            # Estimate revenue (placeholder calculation)
            revenue_opportunity = len(cat_no_rank) * 5000  # ₹5000 per product/month avg
            
            availability.append({
                'category': category,
                'total_products': total_products,
                'amazon_available': amazon_available,
                'amazon_percentage': round((amazon_available / total_products * 100) if total_products > 0 else 0, 1),
                'competitor_availability': dict(list(competitor_avail.items())[:5]),
                'missing_products': missing_products,
                'revenue_opportunity': revenue_opportunity
            })
        
        logger.info(f"✅ Calculated availability for {len(availability)} categories")
        return availability
        
    except Exception as e:
        logger.error(f"❌ Error calculating product availability: {str(e)}")
        raise


def calculate_niche_opportunities() -> List[Dict]:
    """Calculate niche category opportunities"""
    try:
        logger.info("🔄 Calculating niche opportunities...")
        
        df_rankings = load_ranking_data()
        df_no_rank = load_no_rank_data()
        
        opportunities = []
        
        for category in df_rankings['Product'].unique():
            cat_data = df_rankings[df_rankings['Product'] == category]
            amazon_data = cat_data[cat_data['source_normalized'].str.lower() == 'amazon']
            
            if amazon_data.empty:
                continue
            
            amazon_rank = int(amazon_data.iloc[0]['rank'])
            amazon_score = float(amazon_data.iloc[0]['score_norm'])
            
            # Citation frequency (from no-rank data)
            cat_no_rank = df_no_rank[df_no_rank['Product Category'] == category]
            citation_freq = min(100, len(cat_no_rank) * 5)  # Normalized to 100
            
            # Competitor strength (average of top 3)
            top_3_competitors = cat_data[cat_data['rank'] <= 3]
            competitor_strength = float(top_3_competitors['score_norm'].mean() * 100)
            
            # Product gap
            product_gap = len(cat_no_rank)
            
            # Revenue potential (heuristic)
            revenue_potential = min(100, (len(cat_no_rank) * 10 + (5 - amazon_rank) * 10))
            
            # Overall opportunity score
            opportunity_score = (
                (100 - citation_freq) * 0.2 +  # Lower citation = higher opportunity
                (100 - amazon_rank * 20) * 0.3 +  # Better rank = lower opportunity
                (100 - competitor_strength) * 0.3 +  # Weaker competitors = higher opportunity
                revenue_potential * 0.2
            )
            
            quick_win = (amazon_rank in [2, 3]) and (product_gap < 10)
            
            opportunities.append({
                'category': category,
                'citation_frequency': round(citation_freq, 1),
                'amazon_current_rank': amazon_rank,
                'competitor_strength': round(competitor_strength, 1),
                'product_count_gap': product_gap,
                'revenue_potential': round(revenue_potential, 1),
                'opportunity_score': round(opportunity_score, 1),
                'quick_win': quick_win
            })
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: -x['opportunity_score'])
        
        logger.info(f"✅ Identified {len(opportunities)} niche opportunities")
        return opportunities
        
    except Exception as e:
        logger.error(f"❌ Error calculating niche opportunities: {str(e)}")
        raise


def calculate_category_associations() -> List[Dict]:
    """Calculate category association strength"""
    try:
        logger.info("🔄 Calculating category associations...")
        
        df_rankings = load_ranking_data()
        
        associations = []
        
        # Get top marketplaces
        top_marketplaces = df_rankings['source_normalized'].value_counts().head(10).index.tolist()
        
        for marketplace in top_marketplaces:
            mp_data = df_rankings[df_rankings['source_normalized'] == marketplace]
            
            for category in mp_data['Product'].unique()[:15]:  # Top 15 categories
                cat_mp_data = mp_data[mp_data['Product'] == category]
                
                if cat_mp_data.empty:
                    continue
                
                # Win rate (#1 positions)
                win_rate = (cat_mp_data['rank'] == 1).sum() / len(cat_mp_data) * 100
                
                # Top 3 rate
                top_3_rate = (cat_mp_data['rank'] <= 3).sum() / len(cat_mp_data) * 100
                
                # Average score
                avg_score = float(cat_mp_data['score_norm'].mean() * 100)
                
                # Association strength formula
                association_strength = (win_rate * 0.4) + (top_3_rate * 0.3) + (avg_score * 0.3)
                
                # Perception level
                if association_strength >= 70:
                    perception = "Strong"
                elif association_strength >= 40:
                    perception = "Medium"
                else:
                    perception = "Weak"
                
                associations.append({
                    'marketplace': marketplace,
                    'category': category,
                    'win_rate': round(win_rate, 1),
                    'top_3_rate': round(top_3_rate, 1),
                    'avg_score': round(avg_score, 1),
                    'association_strength': round(association_strength, 1),
                    'perception_level': perception
                })
        
        logger.info(f"✅ Calculated {len(associations)} category associations")
        return associations
        
    except Exception as e:
        logger.error(f"❌ Error calculating category associations: {str(e)}")
        raise


def calculate_competitor_specialties() -> List[Dict]:
    """Calculate competitor specialty patterns"""
    try:
        logger.info("🔄 Calculating competitor specialties...")
        
        df_rankings = load_ranking_data()
        
        specialties = []
        
        # Get categories where each competitor is #1
        for competitor in df_rankings['source_normalized'].unique()[:15]:
            if 'amazon' in competitor.lower():
                continue
            
            comp_data = df_rankings[df_rankings['source_normalized'] == competitor]
            dominated = comp_data[comp_data['rank'] == 1]['Product'].tolist()
            
            if not dominated:
                continue
            
            # Calculate average gap to Amazon
            gaps = []
            for category in dominated:
                cat_data = df_rankings[df_rankings['Product'] == category]
                amazon_data = cat_data[cat_data['source_normalized'].str.lower() == 'amazon']
                comp_score = comp_data[comp_data['Product'] == category]['score_norm'].iloc[0]
                
                if not amazon_data.empty:
                    amazon_score = amazon_data.iloc[0]['score_norm']
                    gap = (comp_score - amazon_score) * 100
                    gaps.append(gap)
            
            avg_gap = np.mean(gaps) if gaps else 0
            
            # Determine specialty pattern (heuristic)
            category_keywords = ' '.join(dominated).lower()
            if 'imported' in category_keywords or 'specialty' in category_keywords:
                pattern = "Imported/niche"
            elif 'indian' in category_keywords or 'local' in category_keywords:
                pattern = "Indian mainstream"
            elif 'installation' in category_keywords or 'service' in category_keywords:
                pattern = "Installation-heavy"
            else:
                pattern = "General retail"
            
            action = f"Expand catalog in {pattern} categories" if avg_gap > 15 else "Monitor and maintain"
            
            specialties.append({
                'competitor_name': competitor,
                'dominated_categories': dominated[:10],  # Top 10
                'specialty_pattern': pattern,
                'avg_gap_to_amazon': round(avg_gap, 1),
                'total_wins': len(dominated),
                'action_recommendation': action
            })
        
        # Sort by total wins
        specialties.sort(key=lambda x: -x['total_wins'])
        
        logger.info(f"✅ Identified {len(specialties)} competitor specialties")
        return specialties
        
    except Exception as e:
        logger.error(f"❌ Error calculating competitor specialties: {str(e)}")
        raise


def calculate_intent_alignments() -> List[Dict]:
    """Calculate intent-to-marketplace alignment"""
    try:
        logger.info("🔄 Calculating intent alignments...")
        
        df_rankings = load_ranking_data()
        
        # Define intent categories with keywords
        intents = [
            {'intent': 'Cheapest price', 'keywords': ['price', 'cheap', 'affordable', 'budget']},
            {'intent': 'Fast delivery', 'keywords': ['fast', 'quick', 'delivery', 'shipping']},
            {'intent': 'Authentic product', 'keywords': ['authentic', 'genuine', 'original', 'verified']},
            {'intent': 'Wide selection', 'keywords': ['variety', 'selection', 'choice', 'range']},
            {'intent': 'Professional installation', 'keywords': ['installation', 'service', 'setup', 'professional']},
        ]
        
        alignments = []
        
        for intent_info in intents:
            intent = intent_info['intent']
            
            # Simplified calculation - based on overall marketplace strength
            amazon_wins = len(df_rankings[
                (df_rankings['source_normalized'].str.lower() == 'amazon') &
                (df_rankings['rank'] == 1)
            ])
            total_categories = df_rankings['Product'].nunique()
            amazon_win_rate = (amazon_wins / total_categories * 100) if total_categories > 0 else 0
            
            # Find top competitor
            top_competitors = df_rankings[df_rankings['rank'] == 1]['source_normalized'].value_counts()
            top_competitor = top_competitors.index[0] if len(top_competitors) > 0 else 'N/A'
            competitor_wins = top_competitors.iloc[0] if len(top_competitors) > 0 else 0
            competitor_win_rate = (competitor_wins / total_categories * 100) if total_categories > 0 else 0
            
            # Match strength
            if amazon_win_rate >= 60:
                match_strength = "Strong"
                recommendation = "Maintain leadership"
            elif amazon_win_rate >= 40:
                match_strength = "Medium"
                recommendation = "Strengthen positioning"
            else:
                match_strength = "Weak"
                recommendation = f"Learn from {top_competitor}'s approach"
            
            alignments.append({
                'intent': intent,
                'amazon_win_rate': round(amazon_win_rate, 1),
                'top_competitor': top_competitor,
                'competitor_win_rate': round(competitor_win_rate, 1),
                'match_strength': match_strength,
                'recommendation': recommendation
            })
        
        logger.info(f"✅ Calculated {len(alignments)} intent alignments")
        return alignments
        
    except Exception as e:
        logger.error(f"❌ Error calculating intent alignments: {str(e)}")
        raise


def predict_rank_movement(category: str, products_to_add: int, citations_needed: int) -> Dict:
    """Predict rank movement and ROI (handles cases where Amazon is missing)"""
    try:
        logger.info(f"🔄 Predicting rank for {category}...")
        
        df_rankings = load_ranking_data()
        cat_data = df_rankings[df_rankings['Product'] == category]
        
        if cat_data.empty:
            raise ValueError(f"Category not found: {category}")
        
        amazon_data = cat_data[cat_data['source_normalized'].str.lower() == 'amazon']
        
        # Handle case where Amazon is not in rankings
        if amazon_data.empty:
            logger.warning(f"⚠️ Amazon not found in {category}, using fallback prediction")
            
            # Get rank 1 score for reference
            rank_1_data = cat_data[cat_data['rank'] == 1]
            if not rank_1_data.empty:
                rank_1_score = float(rank_1_data.iloc[0]['score_norm'])
            else:
                rank_1_score = 1.0
            
            # Assume Amazon would start at a low rank if not present
            current_rank = len(cat_data) + 1  # One position below last
            current_score = 0.0  # No current presence
            
            # More aggressive prediction for new entry
            score_boost_from_products = products_to_add * 0.03  # 3% per product
            score_boost_from_citations = citations_needed * 0.02  # 2% per citation
            
            predicted_score = min(1.0, score_boost_from_products + score_boost_from_citations)
            
            # Calculate predicted rank based on score
            better_than = (cat_data['score_norm'] < predicted_score).sum()
            predicted_rank = len(cat_data) - better_than + 1
            predicted_rank = max(1, min(predicted_rank, len(cat_data)))
            
            gap_reduction = (rank_1_score - predicted_score) * 100
            
            # Timeline estimation (longer for new entry)
            estimated_timeline = max(6, int(products_to_add / 2 + citations_needed / 1.5))
            
            # Revenue impact (conservative for new entry)
            revenue_impact = products_to_add * 5000 + (current_rank - predicted_rank) * 10000
            
            # Investment required
            investment = products_to_add * 2000 + citations_needed * 5000
            
            # ROI
            roi_multiplier = (revenue_impact * 12 / investment) if investment > 0 else 0
            
            result = {
                'category': category,
                'current_rank': current_rank,
                'predicted_rank': predicted_rank,
                'gap_reduction': round(gap_reduction, 1),
                'citations_needed': citations_needed,
                'estimated_timeline_months': estimated_timeline,
                'revenue_impact_monthly': revenue_impact,
                'investment_required': investment,
                'roi_multiplier': round(roi_multiplier, 2)
            }
            
            logger.info(f"✅ Predicted (new entry): Unranked → #{predicted_rank} in {estimated_timeline} months")
            return result
        
        # Original logic for existing Amazon ranking
        current_rank = int(amazon_data.iloc[0]['rank'])
        current_score = float(amazon_data.iloc[0]['score_norm'])
        
        # Get #1 score
        rank_1_score = float(cat_data[cat_data['rank'] == 1].iloc[0]['score_norm'])
        
        # Calculate gap
        gap_percentage = (rank_1_score - current_score) * 100
        
        # Prediction logic
        score_boost_from_products = products_to_add * 0.02  # 2% per product
        score_boost_from_citations = citations_needed * 0.01  # 1% per citation
        
        predicted_score = min(1.0, current_score + score_boost_from_products + score_boost_from_citations)
        predicted_rank = max(1, current_rank - int((predicted_score - current_score) / 0.05))
        
        gap_reduction = (rank_1_score - predicted_score) * 100
        
        # Timeline estimation
        estimated_timeline = max(3, int(products_to_add / 3 + citations_needed / 2))
        
        # Revenue impact (heuristic)
        revenue_impact = products_to_add * 8000 + (current_rank - predicted_rank) * 15000
        
        # Investment required
        investment = products_to_add * 2000 + citations_needed * 5000
        
        # ROI
        roi_multiplier = (revenue_impact * 12 / investment) if investment > 0 else 0
        
        result = {
            'category': category,
            'current_rank': current_rank,
            'predicted_rank': predicted_rank,
            'gap_reduction': round(gap_reduction, 1),
            'citations_needed': citations_needed,
            'estimated_timeline_months': estimated_timeline,
            'revenue_impact_monthly': revenue_impact,
            'investment_required': investment,
            'roi_multiplier': round(roi_multiplier, 2)
        }
        
        logger.info(f"✅ Predicted rank: {current_rank} → {predicted_rank} in {estimated_timeline} months")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error predicting rank movement: {str(e)}")
        raise
