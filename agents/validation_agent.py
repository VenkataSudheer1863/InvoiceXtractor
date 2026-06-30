"""Validation and Confidence Scoring Agent"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from config.sap_schema import SAP_COLUMNS, PDF_PRESENT_FIELDS, OPTIONAL_FIELDS

class ValidationAgent(BaseAgent):
    """Agent responsible for validating data and calculating confidence scores"""
    
    def __init__(self):
        super().__init__("ValidationAgent")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate SAP JSON and calculate confidence
        
        Args:
            input_data: {
                "sap_json": Dict,
                "raw_json": Dict
            }
        
        Returns:
            {
                "confidence_score": float,
                "validation_report": Dict,
                "issues": List[str],
                "warnings": List[str]
            }
        """
        sap_json = input_data.get("sap_json", {})
        raw_json = input_data.get("raw_json", {})
        
        try:
            issues = []
            warnings = []
            field_scores = {}
            
            invoices = sap_json.get("invoices", [])
            
            if not invoices:
                issues.append("No invoices found in SAP JSON")
                return {
                    "confidence_score": 0.0,
                    "validation_report": {},
                    "issues": issues,
                    "warnings": warnings,
                    "status": "failed"
                }
            
            # Validate each invoice
            for idx, invoice in enumerate(invoices):
                header = invoice.get("header", {})
                line_items = invoice.get("line_items", [])
                
                # Check required header fields
                required_header = ["BELNR", "BLDAT", "WAERS"]
                for field in required_header:
                    if not header.get(field):
                        issues.append(f"Invoice {idx+1}: Missing required header field {field}")
                        field_scores[field] = 0.0
                    else:
                        field_scores[field] = 1.0
                
                # Check line items
                if not line_items:
                    issues.append(f"Invoice {idx+1}: No line items found")
                
                for item_idx, item in enumerate(line_items):
                    # Check required line item fields
                    required_line = ["WRBTR", "SGTXT"]
                    for field in required_line:
                        if not item.get(field):
                            warnings.append(f"Invoice {idx+1}, Line {item_idx+1}: Missing {field}")
                            field_scores[f"{field}_{item_idx}"] = 0.5
                        else:
                            field_scores[f"{field}_{item_idx}"] = 1.0
                    
                    # Validate numeric fields
                    numeric_fields = ["WRBTR", "Steuerbetrag", "MENGE", "Betrag in HW", "Tage"]
                    for field in numeric_fields:
                        value = item.get(field)
                        if value and not isinstance(value, (int, float)):
                            issues.append(f"Invoice {idx+1}, Line {item_idx+1}: {field} is not numeric")
                    
                    # Validate date fields
                    date_fields = ["BUDAT", "BLDAT", "BZDAT", "ZFBDT"]
                    for field in date_fields:
                        value = item.get(field) or header.get(field)
                        if value and not self._is_valid_date(value):
                            issues.append(f"Invoice {idx+1}: {field} has invalid date format")
            
            # Calculate confidence score
            if field_scores:
                confidence_score = sum(field_scores.values()) / len(field_scores)
            else:
                confidence_score = 0.5
            
            # Adjust for issues
            if issues:
                confidence_score *= 0.7
            if warnings:
                confidence_score *= 0.9
            
            validation_report = {
                "total_invoices": len(invoices),
                "total_line_items": sum(len(inv.get("line_items", [])) for inv in invoices),
                "required_fields_present": len([s for s in field_scores.values() if s == 1.0]),
                "total_fields_checked": len(field_scores),
                "issues_count": len(issues),
                "warnings_count": len(warnings)
            }
            
            self.log_info(f"Validation complete. Confidence: {confidence_score:.2%}")
            
            return {
                "confidence_score": round(confidence_score, 3),
                "validation_report": validation_report,
                "issues": issues,
                "warnings": warnings,
                "status": "success"
            }
        
        except Exception as e:
            self.log_error(f"Validation failed: {e}")
            return {
                "confidence_score": 0.0,
                "validation_report": {},
                "issues": [str(e)],
                "warnings": [],
                "status": "failed"
            }
    
    def _is_valid_date(self, date_str: str) -> bool:
        """Check if date string is in YYYY-MM-DD format"""
        if not isinstance(date_str, str):
            return False
        
        parts = date_str.split("-")
        if len(parts) != 3:
            return False
        
        try:
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            return 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31
        except:
            return False
