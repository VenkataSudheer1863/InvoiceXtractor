"""Date utility functions"""
from datetime import datetime, timedelta
from typing import Optional

def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string in various formats to datetime"""
    if not date_str:
        return None
    
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d.%m.%Y",
        "%Y.%m.%d",
        "%B %d, %Y",
        "%d %B %Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except:
            continue
    
    return None

def format_date_iso(date_str: str) -> str:
    """Convert date string to ISO format (YYYY-MM-DD)"""
    dt = parse_date(date_str)
    if dt:
        return dt.strftime("%Y-%m-%d")
    return ""

def calculate_payment_days(start_date: str, end_date: str) -> int:
    """Calculate number of days between two dates"""
    dt_start = parse_date(start_date)
    dt_end = parse_date(end_date)
    
    if dt_start and dt_end:
        delta = dt_end - dt_start
        return max(0, delta.days)
    
    return 0

def get_current_date_iso() -> str:
    """Get current date in ISO format"""
    return datetime.now().strftime("%Y-%m-%d")
