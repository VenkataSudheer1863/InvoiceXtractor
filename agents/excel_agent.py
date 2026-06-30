"""Excel Generation and Manipulation Agent"""
import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any, List
from openpyxl import load_workbook
from .base_agent import BaseAgent
from config.sap_schema import SAP_COLUMNS, DEFAULT_VALUES

class ExcelAgent(BaseAgent):
    """Agent responsible for Excel file generation and manipulation"""
    
    def __init__(self):
        super().__init__("ExcelAgent")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate or update Excel file from SAP JSON
        
        Args:
            input_data: {
                "sap_json": Dict,
                "base_excel_path": str (optional),
                "output_path": str
            }
        
        Returns:
            {
                "output_path": str,
                "num_rows_added": int,
                "new_rows": List[Dict],
                "operation": str ("updated" or "created")
            }
        """
        sap_json = input_data.get("sap_json", {})
        base_excel_path = input_data.get("base_excel_path")
        output_path = input_data.get("output_path", "output_invoice.xlsx")
        
        try:
            # Convert SAP JSON to rows
            new_rows = self._sap_json_to_rows(sap_json)
            
            if not new_rows:
                self.log_warning("No rows to add")
                return {
                    "output_path": output_path,
                    "num_rows_added": 0,
                    "new_rows": [],
                    "operation": "no_data",
                    "status": "no_data"
                }
            
            # Determine operation type
            is_updating_existing = (base_excel_path and 
                                  os.path.exists(base_excel_path) and 
                                  os.path.abspath(base_excel_path) == os.path.abspath(output_path))
            
            # Load or create Excel
            if base_excel_path and os.path.exists(base_excel_path):
                df_existing = pd.read_excel(base_excel_path)
                existing_rows = len(df_existing)
                self.log_info(f"Loaded existing Excel with {existing_rows} rows from {base_excel_path}")
                operation = "updated" if is_updating_existing else "created_from_template"
            else:
                df_existing = pd.DataFrame(columns=SAP_COLUMNS)
                existing_rows = 0
                self.log_info("Created new Excel file structure")
                operation = "created"
            
            # Append new rows
            df_new = pd.DataFrame(new_rows)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            
            # Create backup if updating existing file
            if is_updating_existing:
                backup_path = f"{base_excel_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df_existing.to_excel(backup_path, index=False, engine='openpyxl')
                self.log_info(f"Created backup: {backup_path}")
            
            # Save to Excel
            df_combined.to_excel(output_path, index=False, engine='openpyxl')
            
            total_rows = len(df_combined)
            new_rows_count = len(new_rows)
            
            if is_updating_existing:
                self.log_info(f"Updated existing Excel file: {output_path}")
                self.log_info(f"Added {new_rows_count} new rows (total: {existing_rows} → {total_rows})")
            else:
                self.log_info(f"Created new Excel file: {output_path}")
                self.log_info(f"Added {new_rows_count} rows to new file (total: {total_rows})")
            
            return {
                "output_path": output_path,
                "num_rows_added": new_rows_count,
                "new_rows": new_rows,
                "operation": operation,
                "total_rows": total_rows,
                "existing_rows": existing_rows,
                "backup_created": is_updating_existing,
                "status": "success"
            }
        
        except Exception as e:
            self.log_error(f"Excel operation failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _sap_json_to_rows(self, sap_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert SAP JSON to list of row dictionaries"""
        rows = []
        
        invoices = sap_json.get("invoices", [])
        
        for invoice in invoices:
            header = invoice.get("header", {})
            line_items = invoice.get("line_items", [])
            
            for line_item in line_items:
                # Merge header and line item
                row = {}
                
                # Add all SAP columns
                for col in SAP_COLUMNS:
                    # Check header first, then line item, then default
                    if col in header:
                        row[col] = header[col]
                    elif col in line_item:
                        row[col] = line_item[col]
                    elif col in DEFAULT_VALUES:
                        row[col] = DEFAULT_VALUES[col]
                    else:
                        row[col] = ""
                
                rows.append(row)
        
        self.log_info(f"Converted {len(invoices)} invoice(s) to {len(rows)} row(s)")
        return rows
