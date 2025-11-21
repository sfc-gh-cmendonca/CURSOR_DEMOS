"""
Dynamic Date Generation Utilities
Never hardcode dates - always generate dynamically relative to current date
"""
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Tuple
from config import DataEngDemoConfig


def get_date_range(days_back: int = None) -> Tuple[str, str]:
    """
    Get date range from N days ago to today
    
    Args:
        days_back: Number of days to go back (uses config default if None)
    
    Returns:
        Tuple of (start_date, end_date) as strings in YYYY-MM-DD format
    
    Example:
        >>> start, end = get_date_range(365)
        >>> print(f"Range: {start} to {end}")
    """
    if days_back is None:
        days_back = DataEngDemoConfig.HISTORICAL_DAYS
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


def get_quarterly_dates(num_quarters: int = 4) -> List[str]:
    """
    Get list of quarter-end dates going back N quarters
    
    Args:
        num_quarters: Number of quarters to generate
    
    Returns:
        List of quarter-end dates in YYYY-MM-DD format
    
    Example:
        >>> quarters = get_quarterly_dates(4)
        >>> print(quarters)  # ['2024-12-31', '2024-09-30', '2024-06-30', '2024-03-31']
    """
    today = datetime.now()
    quarters = []
    
    # Determine the most recent quarter end
    current_quarter = (today.month - 1) // 3
    quarter_ends = [
        datetime(today.year, 3, 31),
        datetime(today.year, 6, 30),
        datetime(today.year, 9, 30),
        datetime(today.year, 12, 31)
    ]
    
    # Find the most recent completed quarter
    recent_quarter_end = None
    for qe in reversed(quarter_ends):
        if qe <= today:
            recent_quarter_end = qe
            break
    
    if recent_quarter_end is None:
        # If we're in Q1 and no quarters completed this year, use last year's Q4
        recent_quarter_end = datetime(today.year - 1, 12, 31)
    
    # Generate N quarters going backwards
    for i in range(num_quarters):
        quarter_date = recent_quarter_end - relativedelta(months=3 * i)
        quarters.append(quarter_date.strftime('%Y-%m-%d'))
    
    return quarters


def get_date_list(start_date: str, end_date: str) -> List[str]:
    """
    Generate list of all dates between start and end (inclusive)
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        List of dates in YYYY-MM-DD format
    
    Example:
        >>> dates = get_date_list('2024-01-01', '2024-01-05')
        >>> len(dates)  # 5
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    date_list = []
    current = start
    while current <= end:
        date_list.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    return date_list


def get_month_list(num_months: int = 12) -> List[str]:
    """
    Get list of month-end dates going back N months
    
    Args:
        num_months: Number of months to generate
    
    Returns:
        List of month-end dates in YYYY-MM-DD format
    
    Example:
        >>> months = get_month_list(6)
        >>> print(months)  # Last 6 month-ends
    """
    today = datetime.now()
    months = []
    
    for i in range(num_months):
        # Go back i months
        month_date = today - relativedelta(months=i)
        # Get last day of that month
        next_month = month_date.replace(day=28) + timedelta(days=4)
        last_day = next_month - timedelta(days=next_month.day)
        months.append(last_day.strftime('%Y-%m-%d'))
    
    return months


def format_timestamp(dt: datetime = None) -> str:
    """
    Format datetime as Snowflake-compatible timestamp string
    
    Args:
        dt: Datetime object (uses current time if None)
    
    Returns:
        Timestamp string in 'YYYY-MM-DD HH:MI:SS' format
    
    Example:
        >>> ts = format_timestamp()
        >>> print(ts)  # '2025-11-18 14:30:00'
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def get_business_days(start_date: str, end_date: str) -> List[str]:
    """
    Generate list of business days (Mon-Fri) between dates
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        List of business days in YYYY-MM-DD format
    
    Example:
        >>> biz_days = get_business_days('2024-01-01', '2024-01-10')
    """
    all_dates = get_date_list(start_date, end_date)
    business_days = []
    
    for date_str in all_dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        # Monday = 0, Sunday = 6
        if date_obj.weekday() < 5:
            business_days.append(date_str)
    
    return business_days

