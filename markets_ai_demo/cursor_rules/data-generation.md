# Guidelines for Synthetic Data Generation Ensuring Realistic Correlations

## Core Principles for Realistic Data Generation

### Financial Data Correlation Rules
- **Revenue and Market Cap**: Larger companies should have proportionally higher revenue
- **EPS and Stock Price**: Generally positive correlation between earnings performance and stock valuation
- **Sector Consistency**: Companies in same sector should have similar margin patterns and growth rates
- **Temporal Consistency**: Financial metrics should follow realistic quarter-over-quarter patterns
- **Market Event Impact**: External events should affect related companies and sectors appropriately

### Dynamic Date Generation (CRITICAL)
**NEVER use hardcoded dates** - always generate relative to current execution time:

```python
from datetime import datetime, timedelta
import calendar

def get_current_quarter():
    """Get current quarter based on current date"""
    now = datetime.now()
    current_quarter = f"{now.year}Q{(now.month-1)//3 + 1}"
    return current_quarter

def get_historical_quarters(num_quarters=4):
    """Generate historical quarters ending with most recent complete quarter"""
    now = datetime.now()
    quarters = []
    
    # Start from previous quarter (assuming current quarter not yet complete)
    year = now.year
    quarter = ((now.month-1)//3 + 1) - 1
    
    if quarter == 0:
        quarter = 4
        year -= 1
    
    for i in range(num_quarters):
        quarters.append(f"{year}Q{quarter}")
        quarter -= 1
        if quarter == 0:
            quarter = 4
            year -= 1
    
    return list(reversed(quarters))

def get_earnings_dates(quarters):
    """Generate realistic earnings announcement dates"""
    earnings_dates = {}
    for quarter in quarters:
        year, q = quarter.split('Q')
        year = int(year)
        q = int(q)
        
        # Earnings typically announced 4-6 weeks after quarter end
        if q == 1:  # Q1 ends March 31
            base_date = datetime(year, 4, 15)
        elif q == 2:  # Q2 ends June 30
            base_date = datetime(year, 7, 15)
        elif q == 3:  # Q3 ends September 30
            base_date = datetime(year, 10, 15)
        else:  # Q4 ends December 31
            base_date = datetime(year + 1, 1, 15)
        
        # Add random variation (0-14 days)
        import random
        earnings_dates[quarter] = base_date + timedelta(days=random.randint(0, 14))
    
    return earnings_dates
```

### Company Hierarchy and Scaling
```python
COMPANY_TIERS = {
    'AAPL': {'tier': 'mega_cap', 'base_revenue': 90000, 'base_market_cap': 1000},
    'MSFT': {'tier': 'mega_cap', 'base_revenue': 50000, 'base_market_cap': 500},
    'GOOGL': {'tier': 'large_cap', 'base_revenue': 30000, 'base_market_cap': 200},
    'NVDA': {'tier': 'large_cap', 'base_revenue': 25000, 'base_market_cap': 200},
    'TSLA': {'tier': 'large_cap', 'base_revenue': 20000, 'base_market_cap': 200},
    'META': {'tier': 'large_cap', 'base_revenue': 28000, 'base_market_cap': 200},
    'SNOW': {'tier': 'mid_cap', 'base_revenue': 2000, 'base_market_cap': 50}
}

def generate_scaled_metrics(ticker, base_metrics, growth_factor=1.0):
    """Scale financial metrics based on company tier and growth"""
    company_info = COMPANY_TIERS[ticker]
    tier_multiplier = {'mega_cap': 1.0, 'large_cap': 0.7, 'mid_cap': 0.3}[company_info['tier']]
    
    return {
        'revenue': base_metrics['revenue'] * tier_multiplier * growth_factor,
        'market_cap': company_info['base_market_cap'],
        'eps': base_metrics['revenue'] * 0.15 / 1000  # Realistic EPS calculation
    }
```

### Realistic Financial Patterns

#### Revenue Growth Patterns
```python
def generate_revenue_growth(base_revenue, quarters, ticker):
    """Generate realistic quarter-over-quarter revenue growth"""
    revenues = []
    
    # Tech sector typical growth rates
    growth_rates = {
        'AAPL': [0.02, 0.08, 0.05, 0.12],    # Seasonal iPhone cycles
        'MSFT': [0.06, 0.07, 0.06, 0.08],    # Steady cloud growth
        'GOOGL': [0.05, 0.04, 0.06, 0.07],   # Advertising cycles
        'NVDA': [0.15, 0.20, 0.18, 0.25],    # High AI-driven growth
        'TSLA': [0.08, 0.12, 0.10, 0.15],    # Variable production cycles
        'META': [0.03, 0.05, 0.04, 0.06],    # Maturing platform
        'SNOW': [0.20, 0.25, 0.22, 0.28]     # High growth SaaS
    }
    
    company_growth = growth_rates.get(ticker, [0.05, 0.06, 0.05, 0.07])
    
    for i, quarter in enumerate(quarters):
        if i == 0:
            revenues.append(base_revenue)
        else:
            growth_rate = company_growth[i % 4]
            # Add random variation ±2%
            import random
            variation = random.uniform(-0.02, 0.02)
            revenues.append(revenues[-1] * (1 + growth_rate + variation))
    
    return revenues
```

#### Analyst Estimates and Surprises
```python
def generate_analyst_estimates(actual_values, surprise_tendency='mixed'):
    """Generate realistic analyst estimates with appropriate surprise patterns"""
    estimates = []
    surprises = []
    
    for actual in actual_values:
        # Analysts typically underestimate high-growth companies
        if surprise_tendency == 'positive_bias':
            estimate = actual * random.uniform(0.92, 0.98)
        elif surprise_tendency == 'negative_bias':
            estimate = actual * random.uniform(1.02, 1.08)
        else:  # mixed
            estimate = actual * random.uniform(0.95, 1.05)
        
        surprise_pct = ((actual - estimate) / estimate) * 100
        
        estimates.append(estimate)
        surprises.append(surprise_pct)
    
    return estimates, surprises
```

### Unstructured Content Generation

#### Earnings Call Transcript Templates
```python
TRANSCRIPT_TEMPLATES = {
    'positive_results': """
    Thank you for joining us today. We're pleased to report strong Q{quarter} results that exceeded our expectations.
    
    Revenue of ${revenue:.1f} million represents {growth:.1f}% growth year-over-year, driven by {key_driver}.
    Our {business_segment} segment continues to show robust demand, with {specific_metric}.
    
    Looking ahead, we remain optimistic about {future_opportunity} and expect continued momentum in {growth_area}.
    We're raising our guidance for {guidance_period} based on these strong fundamentals.
    """,
    
    'mixed_results': """
    Thank you for joining our Q{quarter} earnings call. We delivered solid results despite a challenging environment.
    
    Revenue of ${revenue:.1f} million was in line with expectations, though we saw some headwinds in {challenge_area}.
    Our {strength_area} business performed well, offsetting softness in {weak_area}.
    
    We're taking proactive steps to address {challenge} while continuing to invest in {investment_area}.
    For the next quarter, we expect {cautious_guidance} as we navigate {market_condition}.
    """,
    
    'transformation_story': """
    Good afternoon everyone. Q{quarter} represents another milestone in our {transformation_theme} journey.
    
    Revenue of ${revenue:.1f} million reflects our strategic shift toward {new_focus_area}.
    We're seeing strong adoption of {new_product} with {adoption_metric}.
    
    Our investment in {technology_area} is paying dividends, as evidenced by {success_metric}.
    We remain committed to {long_term_strategy} and expect {future_benefits} over the coming quarters.
    """
}

def generate_earnings_transcript(ticker, quarter, financial_data):
    """Generate realistic earnings call transcript"""
    import random
    
    # Select template based on performance
    revenue_surprise = financial_data['revenue_surprise_percent']
    if revenue_surprise > 3:
        template_type = 'positive_results'
    elif revenue_surprise < -2:
        template_type = 'mixed_results'
    else:
        template_type = random.choice(['positive_results', 'mixed_results'])
    
    # Company-specific context
    context = get_company_context(ticker)
    
    template = TRANSCRIPT_TEMPLATES[template_type]
    return template.format(
        quarter=quarter,
        revenue=financial_data['revenue_millions'],
        growth=financial_data.get('yoy_growth', 5.0),
        **context
    )

def get_company_context(ticker):
    """Get company-specific business context"""
    contexts = {
        'AAPL': {
            'key_driver': 'strong iPhone sales and services growth',
            'business_segment': 'Services',
            'specific_metric': 'record App Store revenue',
            'future_opportunity': 'AI integration across our ecosystem',
            'growth_area': 'emerging markets'
        },
        'NVDA': {
            'key_driver': 'unprecedented AI demand',
            'business_segment': 'Data Center',
            'specific_metric': 'triple-digit growth in AI workloads',
            'future_opportunity': 'generative AI adoption',
            'growth_area': 'enterprise AI solutions'
        },
        'SNOW': {
            'key_driver': 'data cloud platform expansion',
            'business_segment': 'consumption-based',
            'specific_metric': 'strong net revenue retention',
            'future_opportunity': 'AI-powered analytics',
            'growth_area': 'international markets'
        }
    }
    return contexts.get(ticker, {
        'key_driver': 'solid execution',
        'business_segment': 'core',
        'specific_metric': 'steady growth',
        'future_opportunity': 'market expansion',
        'growth_area': 'new initiatives'
    })
```

### Research Report Generation Patterns

#### Investment Theme Templates
```python
RESEARCH_THEMES = {
    'Artificial Intelligence': {
        'thesis': 'AI transformation driving unprecedented demand for compute infrastructure',
        'beneficiaries': ['NVDA', 'MSFT', 'GOOGL'],
        'risks': ['regulatory concerns', 'high valuations', 'competition'],
        'price_targets': {'NVDA': 850, 'MSFT': 420, 'GOOGL': 155}
    },
    'Data Cloud Platform': {
        'thesis': 'Enterprise data modernization creating multi-trillion dollar opportunity',
        'beneficiaries': ['SNOW', 'MSFT', 'GOOGL'],
        'risks': ['increased competition', 'macro headwinds', 'customer concentration'],
        'price_targets': {'SNOW': 200, 'MSFT': 380, 'GOOGL': 145}
    },
    'Consumer Technology': {
        'thesis': 'Device refresh cycles and services monetization driving sustainable growth',
        'beneficiaries': ['AAPL', 'META', 'TSLA'],
        'risks': ['China exposure', 'hardware saturation', 'regulatory pressure'],
        'price_targets': {'AAPL': 195, 'META': 320, 'TSLA': 250}
    }
}
```

### Cross-Reference Consistency Rules

#### Market Events Impact
```python
def apply_market_event_impact(base_data, event, affected_tickers):
    """Apply consistent impact across related companies"""
    impact_factors = {
        'Fed Rate Decision': {'impact': 0.95, 'reason': 'higher discount rates'},
        'AI Chip Regulations': {'impact': 0.92, 'reason': 'regulatory uncertainty'},
        'Cloud Security Breach': {'impact': 0.88, 'reason': 'security concerns'},
        'Tech Earnings Season': {'impact': 1.05, 'reason': 'sector optimism'},
        'AI Breakthrough': {'impact': 1.12, 'reason': 'technology advancement'}
    }
    
    if event in impact_factors and any(ticker in affected_tickers for ticker in base_data.keys()):
        factor = impact_factors[event]
        for ticker in affected_tickers:
            if ticker in base_data:
                base_data[ticker]['market_sentiment'] = factor['impact']
                base_data[ticker]['event_reason'] = factor['reason']
    
    return base_data
```

### Data Quality Validation

#### Consistency Checks
```python
def validate_data_consistency(generated_data):
    """Validate realistic relationships in generated data"""
    issues = []
    
    for ticker, data in generated_data.items():
        # Revenue vs Market Cap reasonableness
        revenue_mc_ratio = data['market_cap_billions'] * 1000 / data['revenue_millions']
        if revenue_mc_ratio < 0.5 or revenue_mc_ratio > 50:
            issues.append(f"{ticker}: Unrealistic market cap to revenue ratio")
        
        # EPS vs Revenue consistency
        implied_shares = data['revenue_millions'] * 0.15 / data['earnings_per_share']
        if implied_shares < 100 or implied_shares > 10000:
            issues.append(f"{ticker}: Inconsistent EPS calculation")
        
        # Surprise magnitude reasonableness
        if abs(data['revenue_surprise_percent']) > 20:
            issues.append(f"{ticker}: Extreme revenue surprise")
    
    return issues

def ensure_temporal_consistency(quarterly_data):
    """Ensure realistic quarter-over-quarter progression"""
    for ticker in quarterly_data:
        revenues = [q['revenue'] for q in quarterly_data[ticker]]
        for i in range(1, len(revenues)):
            qoq_growth = (revenues[i] - revenues[i-1]) / revenues[i-1]
            if abs(qoq_growth) > 0.5:  # >50% QoQ change is unrealistic
                # Smooth the progression
                revenues[i] = revenues[i-1] * 1.1  # Cap at 10% growth
    
    return quarterly_data
```
