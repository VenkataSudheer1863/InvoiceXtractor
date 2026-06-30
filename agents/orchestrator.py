"""Orchestrator Agent - Coordinates all agents"""
import json
import os
from datetime import datetime
from typing import Dict, Any
from .base_agent import BaseAgent
from .pdf_agent import PDFAgent
from .llm_agent import LLMAgent
from .excel_agent import ExcelAgent
from .validation_agent import ValidationAgent

class OrchestratorAgent(BaseAgent):
    """Main orchestrator that coordinates all agents"""
    
    def __init__(self):
        super().__init__("Orchestrator")
        self.pdf_agent = PDFAgent()
        self.llm_agent = LLMAgent()
        self.excel_agent = ExcelAgent()
        self.validation_agent = ValidationAgent()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the entire invoice processing pipeline
        
        Args:
            input_data: {
                "pdf_path": str OR "pdf_paths": List[str],  # Single PDF or multiple PDFs
                "base_excel_path": str (optional),
                "output_dir": str (optional)
            }
        
        Returns:
            {
                "raw_json_path": str,
                "sap_json_path": str,
                "excel_path": str,
                "confidence_report": Dict,
                "new_rows": List[Dict],
                "status": str,
                "processed_files": List[str] (if multiple PDFs)
            }
        """
        pdf_path = input_data.get("pdf_path")
        pdf_paths = input_data.get("pdf_paths")
        
        # Handle multiple PDFs if provided
        if pdf_paths and isinstance(pdf_paths, list) and len(pdf_paths) > 1:
            return self._execute_batch(input_data)
        
        # Handle single PDF (existing logic)
        if pdf_paths and isinstance(pdf_paths, list) and len(pdf_paths) == 1:
            pdf_path = pdf_paths[0]
        
        if not pdf_path:
            return {"error": "No PDF path provided", "status": "failed"}
        
        return self._execute_single(pdf_path, input_data)
    
    def _execute_single(self, pdf_path: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pipeline for a single PDF (original logic preserved)"""
        base_excel_path = input_data.get("base_excel_path", "consolidated_acss_invoices_sample_output.xlsx")
        output_dir = input_data.get("output_dir", "output")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Step 1: PDF Extraction
            self.log_info("Step 1: Extracting PDF content")
            pdf_result = self.pdf_agent.execute({"pdf_path": pdf_path})
            
            if pdf_result.get("status") != "success":
                return {"error": "PDF extraction failed", "details": pdf_result}
            
            # Step 2: LLM Processing (Detection + Extraction + Normalization)
            self.log_info("Step 2: LLM processing (detect, extract, normalize)")
            llm_result = self.llm_agent.execute({
                "raw_text": pdf_result["raw_text"],
                "tables": pdf_result.get("tables", [])
            })
            
            if llm_result.get("status") != "success":
                return {"error": "LLM processing failed", "details": llm_result}
            
            raw_json = llm_result["raw_json"]
            sap_json = llm_result["sap_json"]
            
            # Save JSONs
            raw_json_path = os.path.join(output_dir, f"raw_invoice_{timestamp}.json")
            sap_json_path = os.path.join(output_dir, f"sap_invoice_{timestamp}.json")
            
            with open(raw_json_path, "w", encoding="utf-8") as f:
                json.dump(raw_json, f, indent=2, ensure_ascii=False)
            
            with open(sap_json_path, "w", encoding="utf-8") as f:
                json.dump(sap_json, f, indent=2, ensure_ascii=False)
            
            self.log_info(f"Saved JSONs: {raw_json_path}, {sap_json_path}")
            
            # Step 3: Validation
            self.log_info("Step 3: Validating data")
            validation_result = self.validation_agent.execute({
                "sap_json": sap_json,
                "raw_json": raw_json
            })
            
            # Step 4: Excel Generation
            self.log_info("Step 4: Updating Excel file")
            
            # Use base_excel_path as output if specified, otherwise create new timestamped file
            if base_excel_path and os.path.exists(base_excel_path):
                excel_path = base_excel_path  # Update the existing file directly
                self.log_info(f"Updating existing Excel file: {excel_path}")
            else:
                excel_path = os.path.join(output_dir, f"invoice_output_{timestamp}.xlsx")
                self.log_info(f"Creating new Excel file: {excel_path}")
            
            excel_result = self.excel_agent.execute({
                "sap_json": sap_json,
                "base_excel_path": base_excel_path if os.path.exists(base_excel_path) else None,
                "output_path": excel_path
            })
            
            if excel_result.get("status") != "success":
                return {"error": "Excel generation failed", "details": excel_result}
            
            # Step 5: Generate confidence report
            confidence_report_path = os.path.join(output_dir, f"confidence_report_{timestamp}.json")
            with open(confidence_report_path, "w", encoding="utf-8") as f:
                json.dump(validation_result, f, indent=2)
            
            self.log_info("Pipeline completed successfully")
            
            return {
                "raw_json_path": raw_json_path,
                "sap_json_path": sap_json_path,
                "excel_path": excel_path,
                "confidence_report_path": confidence_report_path,
                "confidence_score": validation_result.get("confidence_score", 0),
                "validation_report": validation_result.get("validation_report", {}),
                "new_rows": excel_result.get("new_rows", []),
                "num_rows_added": excel_result.get("num_rows_added", 0),
                "excel_operation": excel_result.get("operation", "unknown"),
                "total_rows": excel_result.get("total_rows", 0),
                "existing_rows": excel_result.get("existing_rows", 0),
                "backup_created": excel_result.get("backup_created", False),
                "issues": validation_result.get("issues", []),
                "warnings": validation_result.get("warnings", []),
                "status": "success"
            }
        
        except Exception as e:
            self.log_error(f"Orchestration failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _execute_batch(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pipeline for multiple PDFs"""
        pdf_paths = input_data.get("pdf_paths", [])
        base_excel_path = input_data.get("base_excel_path", "consolidated_acss_invoices_sample_output.xlsx")
        output_dir = input_data.get("output_dir", "output")
        
        if not pdf_paths:
            return {"error": "No PDF paths provided for batch processing", "status": "failed"}
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.log_info(f"Starting batch processing of {len(pdf_paths)} PDF files")
        
        # Initialize batch results
        batch_results = {
            "processed_files": [],
            "failed_files": [],
            "all_raw_jsons": [],
            "all_sap_jsons": [],
            "total_new_rows": 0,
            "total_invoices": 0,
            "total_line_items": 0,
            "processing_details": []
        }
        
        # Determine Excel path (same logic as single file)
        if base_excel_path and os.path.exists(base_excel_path):
            excel_path = base_excel_path
            self.log_info(f"Will update existing Excel file: {excel_path}")
        else:
            excel_path = os.path.join(output_dir, f"batch_invoice_output_{timestamp}.xlsx")
            self.log_info(f"Will create new Excel file: {excel_path}")
        
        try:
            # Process each PDF file
            for i, pdf_path in enumerate(pdf_paths, 1):
                self.log_info(f"Processing file {i}/{len(pdf_paths)}: {pdf_path}")
                
                file_result = {
                    "pdf_path": pdf_path,
                    "status": "processing",
                    "error": None
                }
                
                try:
                    # Step 1: PDF Extraction
                    self.log_info(f"  Step 1: Extracting PDF content from {os.path.basename(pdf_path)}")
                    pdf_result = self.pdf_agent.execute({"pdf_path": pdf_path})
                    
                    if pdf_result.get("status") != "success":
                        file_result["status"] = "failed"
                        file_result["error"] = f"PDF extraction failed: {pdf_result.get('error', 'Unknown error')}"
                        batch_results["failed_files"].append(file_result)
                        continue
                    
                    # Step 2: LLM Processing
                    self.log_info(f"  Step 2: LLM processing for {os.path.basename(pdf_path)}")
                    llm_result = self.llm_agent.execute({
                        "raw_text": pdf_result["raw_text"],
                        "tables": pdf_result.get("tables", [])
                    })
                    
                    if llm_result.get("status") != "success":
                        file_result["status"] = "failed"
                        file_result["error"] = f"LLM processing failed: {llm_result.get('error', 'Unknown error')}"
                        batch_results["failed_files"].append(file_result)
                        continue
                    
                    raw_json = llm_result["raw_json"]
                    sap_json = llm_result["sap_json"]
                    
                    # Collect JSONs for batch processing
                    batch_results["all_raw_jsons"].append({
                        "file": pdf_path,
                        "data": raw_json
                    })
                    batch_results["all_sap_jsons"].append({
                        "file": pdf_path,
                        "data": sap_json
                    })
                    
                    # Step 3: Validation
                    self.log_info(f"  Step 3: Validating data for {os.path.basename(pdf_path)}")
                    validation_result = self.validation_agent.execute({
                        "sap_json": sap_json,
                        "raw_json": raw_json
                    })
                    
                    # Update batch statistics
                    val_report = validation_result.get("validation_report", {})
                    batch_results["total_invoices"] += val_report.get("total_invoices", 0)
                    batch_results["total_line_items"] += val_report.get("total_line_items", 0)
                    
                    file_result["status"] = "success"
                    file_result["validation_result"] = validation_result
                    file_result["raw_json"] = raw_json
                    file_result["sap_json"] = sap_json
                    
                    batch_results["processed_files"].append(file_result)
                    self.log_info(f"  ✓ Successfully processed {os.path.basename(pdf_path)}")
                    
                except Exception as e:
                    file_result["status"] = "failed"
                    file_result["error"] = str(e)
                    batch_results["failed_files"].append(file_result)
                    self.log_error(f"  ✗ Failed to process {pdf_path}: {e}")
            
            # Step 4: Combine all SAP JSONs and update Excel
            if batch_results["processed_files"]:
                self.log_info("Step 4: Combining data and updating Excel file")
                
                # Combine all SAP JSONs into one
                combined_sap_json = {"invoices": []}
                for file_result in batch_results["processed_files"]:
                    sap_data = file_result["sap_json"]
                    if "invoices" in sap_data:
                        combined_sap_json["invoices"].extend(sap_data["invoices"])
                
                # Update Excel with combined data
                excel_result = self.excel_agent.execute({
                    "sap_json": combined_sap_json,
                    "base_excel_path": base_excel_path if os.path.exists(base_excel_path) else None,
                    "output_path": excel_path
                })
                
                if excel_result.get("status") == "success":
                    batch_results["total_new_rows"] = excel_result.get("num_rows_added", 0)
                    batch_results["excel_result"] = excel_result
                else:
                    return {"error": "Excel generation failed", "details": excel_result, "status": "failed"}
            
            # Step 5: Save batch JSONs and reports
            batch_raw_json_path = os.path.join(output_dir, f"batch_raw_invoices_{timestamp}.json")
            batch_sap_json_path = os.path.join(output_dir, f"batch_sap_invoices_{timestamp}.json")
            batch_report_path = os.path.join(output_dir, f"batch_processing_report_{timestamp}.json")
            
            # Save combined raw JSON
            combined_raw_json = {
                "batch_info": {
                    "total_files": len(pdf_paths),
                    "processed_files": len(batch_results["processed_files"]),
                    "failed_files": len(batch_results["failed_files"]),
                    "timestamp": timestamp
                },
                "files": batch_results["all_raw_jsons"]
            }
            
            with open(batch_raw_json_path, "w", encoding="utf-8") as f:
                json.dump(combined_raw_json, f, indent=2, ensure_ascii=False)
            
            # Save combined SAP JSON
            combined_sap_json_with_info = {
                "batch_info": {
                    "total_files": len(pdf_paths),
                    "processed_files": len(batch_results["processed_files"]),
                    "failed_files": len(batch_results["failed_files"]),
                    "timestamp": timestamp
                },
                "invoices": combined_sap_json.get("invoices", [])
            }
            
            with open(batch_sap_json_path, "w", encoding="utf-8") as f:
                json.dump(combined_sap_json_with_info, f, indent=2, ensure_ascii=False)
            
            # Save batch processing report
            batch_report = {
                "summary": {
                    "total_files": len(pdf_paths),
                    "processed_successfully": len(batch_results["processed_files"]),
                    "failed_files": len(batch_results["failed_files"]),
                    "total_invoices": batch_results["total_invoices"],
                    "total_line_items": batch_results["total_line_items"],
                    "total_new_rows": batch_results["total_new_rows"],
                    "processing_timestamp": timestamp
                },
                "processed_files": [f["pdf_path"] for f in batch_results["processed_files"]],
                "failed_files": [{"file": f["pdf_path"], "error": f["error"]} for f in batch_results["failed_files"]],
                "excel_operation": batch_results.get("excel_result", {}).get("operation", "unknown")
            }
            
            with open(batch_report_path, "w", encoding="utf-8") as f:
                json.dump(batch_report, f, indent=2, ensure_ascii=False)
            
            self.log_info(f"Batch processing completed: {len(batch_results['processed_files'])}/{len(pdf_paths)} files processed successfully")
            
            # Return batch results
            return {
                "raw_json_path": batch_raw_json_path,
                "sap_json_path": batch_sap_json_path,
                "excel_path": excel_path,
                "batch_report_path": batch_report_path,
                "processed_files": len(batch_results["processed_files"]),
                "failed_files": len(batch_results["failed_files"]),
                "total_files": len(pdf_paths),
                "total_invoices": batch_results["total_invoices"],
                "total_line_items": batch_results["total_line_items"],
                "new_rows": batch_results.get("excel_result", {}).get("new_rows", []),
                "num_rows_added": batch_results["total_new_rows"],
                "excel_operation": batch_results.get("excel_result", {}).get("operation", "unknown"),
                "total_rows": batch_results.get("excel_result", {}).get("total_rows", 0),
                "existing_rows": batch_results.get("excel_result", {}).get("existing_rows", 0),
                "backup_created": batch_results.get("excel_result", {}).get("backup_created", False),
                "validation_report": {
                    "total_invoices": batch_results["total_invoices"],
                    "total_line_items": batch_results["total_line_items"]
                },
                "file_details": batch_results["processed_files"] + batch_results["failed_files"],
                "status": "success"
            }
        
        except Exception as e:
            self.log_error(f"Batch processing failed: {e}")
            return {"error": str(e), "status": "failed"}
