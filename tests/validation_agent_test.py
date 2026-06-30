#!/usr/bin/env python3
"""
Test script to demonstrate how the Validation Agent works
and what data type identification mechanisms it uses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.validation_agent import ValidationAgent
from utils.validation_utils import is_valid_currency, is_valid_amount, validate_sap_row
import json

def test_data_type_identification():
    """Test the data type identification mechanisms used by the validation agent"""
    
    print("=" * 80)
    print("VALIDATION AGENT - DATA TYPE IDENTIFICATION MECHANISMS")
    print("=" * 80)
    
    # Initialize validation agent
    validator = ValidationAgent()
    
    print("\n1. NUMERIC DATA TYPE VALIDATION")
    print("-" * 50)
    
    # Test numeric validation using Python's isinstance()
    test_values = [
        ("Valid integer", 1500, True),
        ("Valid float", 1500.50, True),
        ("String number", "1500", False),
        ("String with currency", "1500 USD", False),
        ("Non-numeric string", "abc", False),
        ("None value", None, False),
        ("Boolean", True, False),
        ("List", [1500], False)
    ]
    
    print("Testing isinstance(value, (int, float)) for numeric validation:")
    for description, value, expected in test_values:
        result = isinstance(value, (int, float))
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"  {description:20} | Value: {str(value):15} | Type: {type(value).__name__:10} | Result: {result:5} | {status}")
    
    print("\n2. DATE FORMAT VALIDATION")
    print("-" * 50)
    
    date_test_values = [
        ("Valid ISO date", "2024-03-15", True),
        ("Valid date edge case", "2023-12-31", True),
        ("Invalid format DD/MM/YYYY", "15/03/2024", False),
        ("Invalid format MM-DD-YYYY", "03-15-2024", False),
        ("Invalid month", "2024-13-01", False),
        ("Invalid day", "2024-02-30", False),
        ("Non-string type", 20240315, False),
        ("Empty string", "", False),
        ("None value", None, False),
        ("Invalid year", "1800-01-01", False),
        ("Future year", "2200-01-01", False)
    ]
    
    print("Testing _is_valid_date() method:")
    for description, value, expected in date_test_values:
        result = validator._is_valid_date(value)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"  {description:25} | Value: {str(value):15} | Result: {result:5} | {status}")
    
    print("\n3. CURRENCY VALIDATION (from utils)")
    print("-" * 50)
    
    currency_test_values = [
        ("Valid USD", "USD", True),
        ("Valid AED", "AED", True),
        ("Valid EUR", "EUR", True),
        ("Lowercase", "usd", True),  # Should be converted to uppercase
        ("Too short", "US", False),
        ("Too long", "USDD", False),
        ("With numbers", "US1", False),
        ("Empty string", "", False),
        ("None value", None, False)
    ]
    
    print("Testing is_valid_currency() from utils:")
    for description, value, expected in currency_test_values:
        result = is_valid_currency(value)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"  {description:15} | Value: {str(value):10} | Result: {result:5} | {status}")
    
    print("\n4. AMOUNT VALIDATION (from utils)")
    print("-" * 50)
    
    amount_test_values = [
        ("Valid integer", 1500, True),
        ("Valid float", 1500.50, True),
        ("String number", "1500", True),
        ("String float", "1500.50", True),
        ("Negative number", -100, True),
        ("Zero", 0, True),
        ("Non-numeric string", "abc", False),
        ("Empty string", "", False),
        ("None value", None, False)
    ]
    
    print("Testing is_valid_amount() from utils:")
    for description, value, expected in amount_test_values:
        result = is_valid_amount(value)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"  {description:20} | Value: {str(value):15} | Result: {result:5} | {status}")

def test_validation_process():
    """Test the complete validation process with sample data"""
    
    print("\n" + "=" * 80)
    print("VALIDATION AGENT - COMPLETE VALIDATION PROCESS")
    print("=" * 80)
    
    validator = ValidationAgent()
    
    # Test Case 1: Perfect Invoice
    print("\n1. TESTING PERFECT INVOICE")
    print("-" * 50)
    
    perfect_sap_json = {
        "invoices": [
            {
                "header": {
                    "BELNR": "INV-2024-001",
                    "BLDAT": "2024-03-15",
                    "WAERS": "USD",
                    "BUKRS": "013",
                    "BLART": "KR"
                },
                "line_items": [
                    {
                        "WRBTR": 1500.00,
                        "SGTXT": "Professional Services",
                        "BSCHL": "40",
                        "HKONT": "K0551",
                        "MENGE": 10,
                        "Steuerbetrag": 75.00,
                        "Tage": 30
                    },
                    {
                        "WRBTR": 1575.00,
                        "SGTXT": "Total Invoice",
                        "BSCHL": "31",
                        "HKONT": "5373979"
                    }
                ]
            }
        ]
    }
    
    result = validator.execute({
        "sap_json": perfect_sap_json,
        "raw_json": {}
    })
    
    print(f"Confidence Score: {result['confidence_score']:.1%}")
    print(f"Issues: {len(result['issues'])}")
    print(f"Warnings: {len(result['warnings'])}")
    print(f"Status: {result['status']}")
    print("Validation Report:")
    for key, value in result['validation_report'].items():
        print(f"  {key}: {value}")
    
    # Test Case 2: Invoice with Issues
    print("\n2. TESTING INVOICE WITH ISSUES")
    print("-" * 50)
    
    problematic_sap_json = {
        "invoices": [
            {
                "header": {
                    # Missing BELNR (required)
                    "BLDAT": "invalid-date",  # Invalid date format
                    "WAERS": "USD"
                },
                "line_items": [
                    {
                        "WRBTR": "not-a-number",  # Invalid numeric type
                        # Missing SGTXT (required)
                        "BSCHL": "40",
                        "MENGE": 10.5,
                        "Steuerbetrag": 75.00
                    }
                ]
            }
        ]
    }
    
    result = validator.execute({
        "sap_json": problematic_sap_json,
        "raw_json": {}
    })
    
    print(f"Confidence Score: {result['confidence_score']:.1%}")
    print(f"Issues: {len(result['issues'])}")
    print(f"Warnings: {len(result['warnings'])}")
    print(f"Status: {result['status']}")
    
    print("\nDetailed Issues:")
    for i, issue in enumerate(result['issues'], 1):
        print(f"  {i}. {issue}")
    
    print("\nDetailed Warnings:")
    for i, warning in enumerate(result['warnings'], 1):
        print(f"  {i}. {warning}")
    
    # Test Case 3: Empty Invoice
    print("\n3. TESTING EMPTY INVOICE DATA")
    print("-" * 50)
    
    empty_sap_json = {
        "invoices": []
    }
    
    result = validator.execute({
        "sap_json": empty_sap_json,
        "raw_json": {}
    })
    
    print(f"Confidence Score: {result['confidence_score']:.1%}")
    print(f"Issues: {len(result['issues'])}")
    print(f"Status: {result['status']}")
    if result['issues']:
        print(f"Issue: {result['issues'][0]}")

def test_field_validation_details():
    """Test specific field validation mechanisms"""
    
    print("\n" + "=" * 80)
    print("FIELD-SPECIFIC VALIDATION MECHANISMS")
    print("=" * 80)
    
    print("\n1. REQUIRED HEADER FIELDS")
    print("-" * 50)
    required_header = ["BELNR", "BLDAT", "WAERS"]
    print("Required header fields:", required_header)
    print("Validation method: Check if field exists and has truthy value")
    print("Example: header.get('BELNR') returns None/empty → Issue")
    
    print("\n2. REQUIRED LINE ITEM FIELDS")
    print("-" * 50)
    required_line = ["WRBTR", "SGTXT"]
    print("Required line item fields:", required_line)
    print("Validation method: Check if field exists and has truthy value")
    print("Example: item.get('WRBTR') returns None/empty → Warning")
    
    print("\n3. NUMERIC FIELDS")
    print("-" * 50)
    numeric_fields = ["WRBTR", "Steuerbetrag", "MENGE", "Betrag in HW", "Tage"]
    print("Numeric fields:", numeric_fields)
    print("Validation method: isinstance(value, (int, float))")
    print("Example: WRBTR = '1500' (string) → Issue (not int/float)")
    
    print("\n4. DATE FIELDS")
    print("-" * 50)
    date_fields = ["BUDAT", "BLDAT", "BZDAT", "ZFBDT"]
    print("Date fields:", date_fields)
    print("Validation method: Custom _is_valid_date() function")
    print("Requirements:")
    print("  - Must be string type")
    print("  - Must match YYYY-MM-DD format")
    print("  - Year: 1900-2100")
    print("  - Month: 1-12")
    print("  - Day: 1-31")
    
    print("\n5. CONFIDENCE SCORE CALCULATION")
    print("-" * 50)
    print("Base Score = (Sum of field scores) / (Total fields checked)")
    print("Field Scores:")
    print("  - Present required field: 1.0")
    print("  - Missing optional field: 0.5")
    print("  - Missing required field: 0.0")
    print("Penalties:")
    print("  - Issues present: × 0.7 (30% reduction)")
    print("  - Warnings present: × 0.9 (10% reduction)")
    print("Final Score = Base Score × Issue Penalty × Warning Penalty")

def demonstrate_validation_mechanisms():
    """Demonstrate the actual validation mechanisms in action"""
    
    print("\n" + "=" * 80)
    print("VALIDATION MECHANISMS DEMONSTRATION")
    print("=" * 80)
    
    # 1. Field Existence Check
    print("\n1. FIELD EXISTENCE CHECK")
    print("-" * 30)
    
    test_data = {"BELNR": "INV-001", "WAERS": "USD"}  # Missing BLDAT
    required_fields = ["BELNR", "BLDAT", "WAERS"]
    
    print("Test data:", test_data)
    print("Required fields:", required_fields)
    print("Validation results:")
    
    for field in required_fields:
        exists = bool(test_data.get(field))
        print(f"  {field}: {'✅ Present' if exists else '❌ Missing'}")
    
    # 2. Type Checking
    print("\n2. TYPE CHECKING DEMONSTRATION")
    print("-" * 30)
    
    test_values = {
        "WRBTR_good": 1500.00,
        "WRBTR_bad": "1500",
        "MENGE_good": 10,
        "MENGE_bad": "ten"
    }
    
    print("Test values:", test_values)
    print("Numeric validation results:")
    
    for field, value in test_values.items():
        is_numeric = isinstance(value, (int, float))
        print(f"  {field}: {value} → {'✅ Valid' if is_numeric else '❌ Invalid'} (type: {type(value).__name__})")
    
    # 3. Date Validation
    print("\n3. DATE VALIDATION DEMONSTRATION")
    print("-" * 30)
    
    validator = ValidationAgent()
    test_dates = {
        "valid_date": "2024-03-15",
        "invalid_format": "15/03/2024",
        "invalid_month": "2024-13-01",
        "non_string": 20240315
    }
    
    print("Date validation results:")
    for field, date_value in test_dates.items():
        is_valid = validator._is_valid_date(date_value)
        print(f"  {field}: {date_value} → {'✅ Valid' if is_valid else '❌ Invalid'}")

if __name__ == "__main__":
    print("VALIDATION AGENT COMPREHENSIVE TEST")
    print("This script demonstrates how the Validation Agent identifies data types")
    print("and performs validation to ensure data quality.")
    
    try:
        test_data_type_identification()
        test_validation_process()
        test_field_validation_details()
        demonstrate_validation_mechanisms()
        
        print("\n" + "=" * 80)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()