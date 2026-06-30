"""Validation utility functions"""
import re
from typing import Any

def is_valid_currency(currency: str) -> bool:
    """Check if currency code is valid (3 letters)"""
    if not currency:
        return False
    return bool(re.match(r'^[A-Z]{3}$', str(currency).upper()))

def is_valid_amount(amount: Any) -> bool:
    """Check if amount is a valid number"""
    try:
        float(amount)
        return True
    except:
        return False

def is_valid_quantity(quantity: Any) -> bool:
    """Check if quantity is a valid number"""
    try:
        val = float(quantity)
        return val >= 0
    except:
        return False

def clean_amount(amount_str: str) -> float:
    """Clean and convert amount string to float"""
    if isinstance(amount_str, (int, float)):
        return float(amount_str)
    
    # Remove currency symbols and spaces
    cleaned = str(amount_str).replace(',', '').replace(' ', '')
    cleaned = re.sub(r'[^\d.-]', '', cleaned)
    
    try:
        return float(cleaned)
    except:
        return 0.0

def validate_sap_row(row: dict) -> tuple[bool, list]:
    """Validate a single SAP row"""
    errors = []
    
    # Required fields
    required = ["BELNR", "BLDAT", "WAERS", "WRBTR"]
    for field in required:
        if not row.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Validate amounts
    amount_fields = ["WRBTR", "Steuerbetrag", "Betrag in HW"]
    for field in amount_fields:
        if row.get(field) and not is_valid_amount(row[field]):
            errors.append(f"Invalid amount in {field}")
    
    # Validate currency
    if row.get("WAERS") and not is_valid_currency(row["WAERS"]):
        errors.append(f"Invalid currency: {row['WAERS']}")
    
    return len(errors) == 0, errors
