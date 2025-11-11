import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict
import re
from urllib.parse import urlparse

from app.core.config import settings
from app.core.logger import setup_logger, log_excel_loading
from app.services.analytics import load_ranking_data, load_product_details_data

logger = setup_logger(__name__)


def load_no_rank_data() -> pd.DataFrame:
    """Load products without Amazon presence"""
    try:
        file_path = settings.EXCEL_FILE_3
        
        if not file_path.exists():
            logger.error(f"Excel file not found: {file_path}")
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        df = pd.read_excel(file_path)
        
        log_excel_loading(
            file_path=file_path,
            rows=len(df),
            columns=len(df.columns),
            sheet_name="Sheet1"
        )
        
        logger.info(f"✅ Successfully loaded {len(df)} no-rank products")
        return df
        
    except Exception as e:
        logger.error(f"Error loading no-rank data: {str(e)}")
        raise


def calculate_overview_metrics() -> Dict:
    """Calculate executive dashboard overview metrics"""
    try:
        logger.info("🔄 Calculating overview metrics...")
        
        df = load_ranking_data()
        
        # Total unique categories
        total_categories = df['Product'].nunique()
        
        # Amazon-specific data
        amazon_data = df[df['source_normalized'].str.lower() == 'amazon'].copy()
        
        # Categories where Amazon appears
        amazon_categories = amazon_data['Product'].nunique()
        visibility_score = (amazon_categories / total_categories) * 100
        
        # Categories where Amazon is #1
        categories_rank_1 = len(amazon_data[amazon_data['rank'] == 1])
        market_leadership_score = (categories_rank_1 / total_categories) * 100
        
        # Average ranking
        average_ranking = amazon_data['rank'].mean()
        
        # Opportunity gap
        opportunity_gap = 100 - market_leadership_score
        categories_not_rank_1 = total_categories - categories_rank_1
        
        metrics = {
            'visibility_score': round(visibility_score, 2),
            'market_leadership_score': round(market_leadership_score, 2),
            'average_ranking': round(average_ranking, 2),
            'opportunity_gap': round(opportunity_gap, 2),
            'total_categories': total_categories,
            'categories_rank_1': categories_rank_1,
            'categories_not_rank_1': categories_not_rank_1
        }
        
        logger.info(f"✅ Overview metrics calculated: {metrics}")
        return metrics
        
    except Exception as e:
        logger.error(f"❌ Error calculating overview metrics: {str(e)}")
        raise


def generate_performance_quadrants() -> List[Dict]:
    """Generate 2x2 performance quadrant matrix data"""
    try:
        logger.info("🔄 Generating performance quadrants...")
        
        df_rankings = load_ranking_data()
        df_details = load_product_details_data()
        
        # Get category sizes (product count)
        category_sizes = df_details.groupby('Product')['product_name'].nunique().to_dict()
        
        quadrants = []
        
        for category in df_rankings['Product'].unique():
            cat_data = df_rankings[df_rankings['Product'] == category]
            amazon_data = cat_data[cat_data['source_normalized'].str.lower() == 'amazon']
            
            if not amazon_data.empty:
                amazon_score = amazon_data.iloc[0]['score_norm']
                amazon_rank = amazon_data.iloc[0]['rank']
                category_size = category_sizes.get(category, 1)
                
                # Determine quadrant
                high_score = amazon_score >= 0.15  # Top 50% threshold
                high_importance = category_size >= 3  # High product count
                
                if high_score and high_importance:
                    quadrant = "Stars"
                elif not high_score and high_importance:
                    quadrant = "Question Marks"
                elif high_score and not high_importance:
                    quadrant = "Cash Cows"
                else:
                    quadrant = "Dogs"
                
                quadrants.append({
                    'category': category,
                    'amazon_score': float(amazon_score),
                    'category_size': int(category_size),
                    'amazon_rank': int(amazon_rank),
                    'quadrant': quadrant
                })
        
        logger.info(f"✅ Generated {len(quadrants)} quadrant data points")
        return quadrants
        
    except Exception as e:
        logger.error(f"❌ Error generating performance quadrants: {str(e)}")
        raise


def analyze_competitor_threats() -> List[Dict]:
    """Analyze competitor threat levels"""
    try:
        logger.info("🔄 Analyzing competitor threats...")
        
        df = load_ranking_data()
        
        # Get categories where Amazon is not #1
        competitor_wins = defaultdict(list)
        
        for category in df['Product'].unique():
            cat_data = df[df['Product'] == category].sort_values('rank')
            winner = cat_data.iloc[0]
            
            amazon_data = cat_data[cat_data['source_normalized'].str.lower() == 'amazon']
            
            if not amazon_data.empty and winner['source_normalized'].lower() != 'amazon':
                amazon_score = amazon_data.iloc[0]['score_norm']
                gap_percentage = (winner['score_norm'] - amazon_score) * 100
                
                competitor_wins[winner['source_normalized']].append({
                    'category': category,
                    'gap': gap_percentage
                })
        
        # Aggregate competitor analysis
        threats = []
        for competitor, wins in competitor_wins.items():
            categories_dominated = len(wins)
            average_gap = np.mean([w['gap'] for w in wins])
            dominated_categories = [w['category'] for w in wins]
            
            # Determine threat level
            if average_gap >= 15:
                threat_level = "Critical"
            elif average_gap >= 10:
                threat_level = "High"
            elif average_gap >= 5:
                threat_level = "Medium"
            else:
                threat_level = "Low"
            
            threats.append({
                'competitor_name': competitor,
                'categories_dominated': categories_dominated,
                'average_gap_percentage': round(average_gap, 2),
                'total_wins': categories_dominated,
                'threat_level': threat_level,
                'dominated_categories': dominated_categories
            })
        
        # Sort by threat level and gap
        threats.sort(key=lambda x: (-x['categories_dominated'], -x['average_gap_percentage']))
        
        logger.info(f"✅ Identified {len(threats)} competitor threats")
        return threats
        
    except Exception as e:
        logger.error(f"❌ Error analyzing competitor threats: {str(e)}")
        raise


def categorize_by_priority() -> Dict[str, List[Dict]]:
    """Categorize opportunities by severity (Critical/Medium/Low)"""
    try:
        logger.info("🔄 Categorizing by priority...")
        
        df = load_ranking_data()
        
        critical = []
        medium = []
        low = []
        
        for category in df['Product'].unique():
            cat_data = df[df['Product'] == category].sort_values('rank')
            winner = cat_data.iloc[0]
            amazon_data = cat_data[cat_data['source_normalized'].str.lower() == 'amazon']
            
            if not amazon_data.empty:
                amazon_rank = int(amazon_data.iloc[0]['rank'])
                amazon_score = amazon_data.iloc[0]['score_norm']
                
                if amazon_rank > 1:
                    gap_percentage = (winner['score_norm'] - amazon_score) * 100
                    
                    # Calculate priority score
                    priority_score = min(100, (gap_percentage * 2) + ((amazon_rank - 1) * 10))
                    
                    category_data = {
                        'category': category,
                        'current_rank': amazon_rank,
                        'gap_percentage': round(gap_percentage, 2),
                        'competitor': winner['source_normalized'],
                        'competitor_score': float(winner['score_norm']),
                        'amazon_score': float(amazon_score),
                        'priority_score': round(priority_score, 2)
                    }
                    
                    # Categorize by gap
                    if gap_percentage >= 15:
                        category_data['severity'] = "Critical"
                        critical.append(category_data)
                    elif gap_percentage >= 7:
                        category_data['severity'] = "Medium"
                        medium.append(category_data)
                    else:
                        category_data['severity'] = "Low"
                        low.append(category_data)
        
        result = {
            'critical': sorted(critical, key=lambda x: -x['gap_percentage']),
            'medium': sorted(medium, key=lambda x: -x['gap_percentage']),
            'low': sorted(low, key=lambda x: -x['gap_percentage'])
        }
        
        logger.info(f"✅ Categorized: {len(critical)} Critical, {len(medium)} Medium, {len(low)} Low")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error categorizing by priority: {str(e)}")
        raise


def analyze_no_rank_products() -> Dict:
    """Analyze products where Amazon has no presence"""
    try:
        logger.info("🔄 Analyzing no-rank products...")
        
        df = load_no_rank_data()
        
        total_missing = len(df)
        categories_affected = df['Product Category'].nunique()
        
        # Top opportunity categories by product count
        top_categories = df['Product Category'].value_counts().head(10)
        top_opportunity_categories = [
            {'category': cat, 'product_count': int(count)}
            for cat, count in top_categories.items()
        ]
        
        # Products with citations
        products_with_citations = df['Citations'].notna().sum()
        
        # Sample products
        sample_products = []
        for _, row in df.head(20).iterrows():
            sample_products.append({
                'product_category': row['Product Category'],
                'product_name': row['Product Name'],
                'citations': row['Citations'] if pd.notna(row['Citations']) else None
            })
        
        result = {
            'total_missing_products': total_missing,
            'categories_affected': categories_affected,
            'top_opportunity_categories': top_opportunity_categories,
            'products_with_citations': int(products_with_citations),
            'sample_products': sample_products
        }
        
        logger.info(f"✅ No-rank analysis complete: {total_missing} missing products")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error analyzing no-rank products: {str(e)}")
        raise


def extract_citation_sources() -> List[Dict]:
    """Extract and analyze citation sources"""
    try:
        logger.info("🔄 Extracting citation sources...")
        
        df = load_no_rank_data()
        
        domain_count = defaultdict(lambda: {'count': 0, 'categories': set()})
        
        for _, row in df.iterrows():
            if pd.notna(row['Citations']):
                # Extract URLs from citation string
                urls = re.findall(r'https?://[^\s\]]+', str(row['Citations']))
                
                for url in urls:
                    try:
                        domain = urlparse(url).netloc
                        domain = domain.replace('www.', '')
                        domain_count[domain]['count'] += 1
                        domain_count[domain]['categories'].add(row['Product Category'])
                    except:
                        continue
        
        # Convert to list and calculate impact score
        citations = []
        for domain, data in domain_count.items():
            impact_score = (data['count'] * 0.7) + (len(data['categories']) * 0.3)
            citations.append({
                'domain': domain,
                'frequency': data['count'],
                'categories': sorted(list(data['categories'])),
                'impact_score': round(impact_score, 2)
            })
        
        # Sort by impact score
        citations.sort(key=lambda x: -x['impact_score'])
        
        logger.info(f"✅ Extracted {len(citations)} citation sources")
        return citations[:50]  # Top 50
        
    except Exception as e:
        logger.error(f"❌ Error extracting citation sources: {str(e)}")
        raise


def generate_category_heatmap() -> List[Dict]:
    """Generate category performance heatmap data"""
    try:
        logger.info("🔄 Generating category heatmap...")
        
        df = load_ranking_data()
        
        heatmap = []
        
        for category in sorted(df['Product'].unique()):
            cat_data = df[df['Product'] == category].sort_values('rank')
            winner = cat_data.iloc[0]
            amazon_data = cat_data[cat_data['source_normalized'].str.lower() == 'amazon']
            
            if not amazon_data.empty:
                amazon_rank = int(amazon_data.iloc[0]['rank'])
                amazon_score = float(amazon_data.iloc[0]['score_norm'])
                gap_to_first = float(winner['score_norm'] - amazon_score) if amazon_rank > 1 else 0.0
                
                # Determine color
                if amazon_rank == 1:
                    status_color = "green"
                elif amazon_rank <= 3:
                    status_color = "yellow"
                elif amazon_rank <= 5:
                    status_color = "orange"
                else:
                    status_color = "red"
                
                heatmap.append({
                    'category': category,
                    'amazon_rank': amazon_rank,
                    'amazon_score': round(amazon_score, 4),
                    'gap_to_first': round(gap_to_first, 4),
                    'competitor_name': winner['source_normalized'] if amazon_rank > 1 else 'Amazon',
                    'status_color': status_color
                })
        
        logger.info(f"✅ Generated heatmap for {len(heatmap)} categories")
        return heatmap
        
    except Exception as e:
        logger.error(f"❌ Error generating category heatmap: {str(e)}")
        raise


def identify_quick_wins() -> List[Dict]:
    """Identify quick win opportunities (<15% gap)"""
    try:
        logger.info("🔄 Identifying quick wins...")
        
        df = load_ranking_data()
        
        quick_wins = []
        
        for category in df['Product'].unique():
            cat_data = df[df['Product'] == category].sort_values('rank')
            winner = cat_data.iloc[0]
            amazon_data = cat_data[cat_data['source_normalized'].str.lower() == 'amazon']
            
            if not amazon_data.empty:
                amazon_rank = int(amazon_data.iloc[0]['rank'])
                amazon_score = amazon_data.iloc[0]['score_norm']
                
                if amazon_rank in [2, 3]:
                    gap_percentage = (winner['score_norm'] - amazon_score) * 100
                    
                    if gap_percentage < 15:
                        # Generate action items based on gap
                        action_items = []
                        if gap_percentage < 5:
                            action_items = ["Increase product variety", "Optimize pricing"]
                            effort = "Low"
                        elif gap_percentage < 10:
                            action_items = ["Expand product catalog", "Improve delivery speed", "Enhance reviews"]
                            effort = "Medium"
                        else:
                            action_items = ["Strategic pricing review", "Marketing push", "Partnership opportunities"]
                            effort = "Medium"
                        
                        quick_wins.append({
                            'category': category,
                            'current_rank': amazon_rank,
                            'gap_percentage': round(gap_percentage, 2),
                            'competitor': winner['source_normalized'],
                            'action_items': action_items,
                            'estimated_effort': effort
                        })
        
        # Sort by gap (easiest first)
        quick_wins.sort(key=lambda x: x['gap_percentage'])
        
        logger.info(f"✅ Identified {len(quick_wins)} quick wins")
        return quick_wins
        
    except Exception as e:
        logger.error(f"❌ Error identifying quick wins: {str(e)}")
        raise


def identify_battlegrounds() -> List[Dict]:
    """Identify strategic battleground categories"""
    try:
        logger.info("🔄 Identifying battlegrounds...")
        
        df_rankings = load_ranking_data()
        df_details = load_product_details_data()
        
        # Get category sizes
        category_sizes = df_details.groupby('Product')['product_name'].nunique().to_dict()
        
        battlegrounds = []
        
        for category in df_rankings['Product'].unique():
            cat_data = df_rankings[df_rankings['Product'] == category].sort_values('rank')
            winner = cat_data.iloc[0]
            amazon_data = cat_data[cat_data['source_normalized'].str.lower() == 'amazon']
            
            if not amazon_data.empty:
                amazon_rank = int(amazon_data.iloc[0]['rank'])
                amazon_score = amazon_data.iloc[0]['score_norm']
                product_count = category_sizes.get(category, 0)
                
                if amazon_rank > 1:
                    gap_percentage = (winner['score_norm'] - amazon_score) * 100
                    
                    # Medium gap with potential high volume
                    if 7 <= gap_percentage <= 20:
                        # Determine volume
                        if product_count >= 5:
                            product_volume = "High"
                            investment_priority = "High"
                        elif product_count >= 3:
                            product_volume = "Medium"
                            investment_priority = "Medium"
                        else:
                            product_volume = "Low"
                            investment_priority = "Low"
                        
                        battlegrounds.append({
                            'category': category,
                            'amazon_rank': amazon_rank,
                            'gap_percentage': round(gap_percentage, 2),
                            'competitor': winner['source_normalized'],
                            'product_volume': product_volume,
                            'investment_priority': investment_priority
                        })
        
        # Sort by investment priority
        priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
        battlegrounds.sort(key=lambda x: (-priority_order[x['investment_priority']], -x['gap_percentage']))
        
        logger.info(f"✅ Identified {len(battlegrounds)} battleground categories")
        return battlegrounds
        
    except Exception as e:
        logger.error(f"❌ Error identifying battlegrounds: {str(e)}")
        raise


def get_competitor_details(competitor_name: str) -> Dict:
    """Get detailed analysis for a specific competitor"""
    try:
        logger.info(f"🔄 Getting details for competitor: {competitor_name}")
        
        df = load_ranking_data()
        
        categories = []
        
        for category in df['Product'].unique():
            cat_data = df[df['Product'] == category].sort_values('rank')
            competitor_data = cat_data[cat_data['source_normalized'] == competitor_name]
            amazon_data = cat_data[cat_data['source_normalized'].str.lower() == 'amazon']
            
            if not competitor_data.empty and not amazon_data.empty:
                comp_rank = int(competitor_data.iloc[0]['rank'])
                comp_score = float(competitor_data.iloc[0]['score_norm'])
                amazon_rank = int(amazon_data.iloc[0]['rank'])
                amazon_score = float(amazon_data.iloc[0]['score_norm'])
                gap = (comp_score - amazon_score) * 100
                
                categories.append({
                    'category': category,
                    'rank': comp_rank,
                    'score': round(comp_score, 4),
                    'amazon_rank': amazon_rank,
                    'amazon_score': round(amazon_score, 4),
                    'gap': round(gap, 2)
                })
        
        # Sort by rank (dominance)
        categories.sort(key=lambda x: x['rank'])
        
        # Get categories where competitor is #1
        dominated = [c for c in categories if c['rank'] == 1]
        
        # Calculate average gap
        avg_gap = np.mean([c['gap'] for c in categories]) if categories else 0
        
        # Identify strength areas (categories where competitor beats Amazon significantly)
        strength_areas = [c['category'] for c in categories if c['gap'] > 10]
        
        result = {
            'competitor_name': competitor_name,
            'total_categories_dominated': len(dominated),
            'average_gap': round(avg_gap, 2),
            'categories': categories,
            'strength_areas': strength_areas[:10]  # Top 10
        }
        
        logger.info(f"✅ Retrieved details for {competitor_name}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting competitor details: {str(e)}")
        raise


def get_category_battle_details(category_name: str) -> Dict:
    """Get detailed battle analysis for a specific category"""
    try:
        logger.info(f"🔄 Getting battle details for category: {category_name}")
        
        df_rankings = load_ranking_data()
        df_details = load_product_details_data()
        df_no_rank = load_no_rank_data()
        
        # Get top 5 competitors in this category
        cat_data = df_rankings[df_rankings['Product'] == category_name].sort_values('rank').head(5)
        
        amazon_data = cat_data[cat_data['source_normalized'].str.lower() == 'amazon']
        amazon_rank = int(amazon_data.iloc[0]['rank']) if not amazon_data.empty else 0
        amazon_score = float(amazon_data.iloc[0]['score_norm']) if not amazon_data.empty else 0
        
        top_5_competitors = []
        for _, row in cat_data.iterrows():
            gap = (row['score_norm'] - amazon_score) * 100 if amazon_score > 0 else 0
            top_5_competitors.append({
                'name': row['source_normalized'],
                'rank': int(row['rank']),
                'score': float(row['score_norm']),
                'gap': round(gap, 2)
            })
        
        # Product counts
        cat_details = df_details[df_details['Product'] == category_name]
        total_products = cat_details['product_name'].nunique() if not cat_details.empty else 0
        amazon_products = cat_details[cat_details['source_normalized'].str.lower() == 'amazon']['product_name'].nunique() if not cat_details.empty else 0
        
        # Missing products
        missing = df_no_rank[df_no_rank['Product Category'] == category_name]
        missing_count = len(missing)
        
        result = {
            'category': category_name,
            'amazon_rank': amazon_rank,
            'amazon_score': round(amazon_score, 4),
            'top_5_competitors': top_5_competitors,
            'product_count': int(total_products),
            'amazon_product_count': int(amazon_products),
            'missing_product_count': int(missing_count)
        }
        
        logger.info(f"✅ Retrieved battle details for {category_name}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error getting category battle details: {str(e)}")
        raise
