"""
Example Usage of the Invoice Processing System

This script demonstrates various ways to use the system programmatically.
"""

import os
import json
from agents.orchestrator import OrchestratorAgent
from agents.pdf_agent import PDFAgent
from agents.llm_agent import LLMAgent
from agents.excel_agent import ExcelAgent
from agents.validation_agent import ValidationAgent

# ============================================================================
# Example 1: Simple End-to-End Processing
# ============================================================================

def example_1_simple_processing():
    """Process a single invoice end-to-end"""
    print("=" * 60)
    print("Example 1: Simple End-to-End Processing")
    print("=" * 60)
    
    orchestrator = OrchestratorAgent()
    
    result = orchestrator.execute({
        "pdf_path": "POC_1.pdf",
        "base_excel_path": "consolidated_acss_invoices_sample_output.xlsx",
        "output_dir": "output"
    })
    
    if result["status"] == "success":
        print(f"✅ Success!")
        print(f"Confidence: {result['confidence_score']:.1%}")
        print(f"Rows added: {result['num_rows_added']}")
        print(f"Excel: {result['excel_path']}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    return result


# ============================================================================
# Example 2: Step-by-Step Processing (Manual Agent Control)
# ============================================================================

def example_2_manual_agents():
    """Process invoice step-by-step with manual agent control"""
    print("\n" + "=" * 60)
    print("Example 2: Manual Agent Control")
    print("=" * 60)
    
    pdf_path = "POC_1.pdf"
    
    # Step 1: Extract PDF
    print("\n[1/4] Extracting PDF...")
    pdf_agent = PDFAgent()
    pdf_result = pdf_agent.execute({"pdf_path": pdf_path})
    
    if pdf_result["status"] != "success":
        print(f"❌ PDF extraction failed")
        return
    
    print(f"✅ Extracted {pdf_result['metadata']['num_pages']} pages")
    
    # Step 2: LLM Processing
    print("\n[2/4] Processing with LLM...")
    llm_agent = LLMAgent()
    llm_result = llm_agent.execute({
        "raw_text": pdf_result["raw_text"],
        "tables": pdf_result.get("tables", [])
    })
    
    if llm_result["status"] != "success":
        print(f"❌ LLM processing failed")
        return
    
    print(f"✅ Detected {llm_result['num_invoices']} invoice(s)")
    
    # Step 3: Validation
    print("\n[3/4] Validating...")
    validation_agent = ValidationAgent()
    validation_result = validation_agent.execute({
        "sap_json": llm_result["sap_json"],
        "raw_json": llm_result["raw_json"]
    })
    
    print(f"✅ Confidence: {validation_result['confidence_score']:.1%}")
    
    # Step 4: Generate Excel
    print("\n[4/4] Generating Excel...")
    excel_agent = ExcelAgent()
    excel_result = excel_agent.execute({
        "sap_json": llm_result["sap_json"],
        "output_path": "output/manual_output.xlsx"
    })
    
    if excel_result["status"] == "success":
        print(f"✅ Generated Excel with {excel_result['num_rows_added']} rows")
        print(f"📁 {excel_result['output_path']}")
    
    return {
        "pdf": pdf_result,
        "llm": llm_result,
        "validation": validation_result,
        "excel": excel_result
    }


# ============================================================================
# Example 3: Batch Processing Multiple PDFs
# ============================================================================

def example_3_batch_processing():
    """Process multiple PDFs in batch"""
    print("\n" + "=" * 60)
    print("Example 3: Batch Processing")
    print("=" * 60)
    
    pdf_files = [
        "POC_1.pdf",
        "POC_2.pdf",
        "POC_3.pdf"
    ]
    
    orchestrator = OrchestratorAgent()
    results = []
    
    for idx, pdf_file in enumerate(pdf_files, 1):
        if not os.path.exists(pdf_file):
            print(f"\n[{idx}/{len(pdf_files)}] ⚠️  Skipping {pdf_file} - not found")
            continue
        
        print(f"\n[{idx}/{len(pdf_files)}] Processing {pdf_file}...")
        
        result = orchestrator.execute({
            "pdf_path": pdf_file,
            "output_dir": f"output/batch_{idx}"
        })
        
        if result["status"] == "success":
            print(f"  ✅ Success - Confidence: {result['confidence_score']:.1%}")
            results.append({
                "file": pdf_file,
                "status": "success",
                "confidence": result["confidence_score"],
                "rows": result["num_rows_added"]
            })
        else:
            print(f"  ❌ Failed - {result.get('error')}")
            results.append({
                "file": pdf_file,
                "status": "failed",
                "error": result.get("error")
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("Batch Processing Summary")
    print("=" * 60)
    
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]
    
    print(f"Total: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        avg_confidence = sum(r["confidence"] for r in successful) / len(successful)
        total_rows = sum(r["rows"] for r in successful)
        print(f"Average Confidence: {avg_confidence:.1%}")
        print(f"Total Rows: {total_rows}")
    
    return results


# ============================================================================
# Example 4: Custom Processing with Filtering
# ============================================================================

def example_4_custom_filtering():
    """Process invoice with custom filtering and validation"""
    print("\n" + "=" * 60)
    print("Example 4: Custom Filtering")
    print("=" * 60)
    
    orchestrator = OrchestratorAgent()
    
    result = orchestrator.execute({
        "pdf_path": "POC_1.pdf",
        "output_dir": "output"
    })
    
    if result["status"] != "success":
        print("❌ Processing failed")
        return
    
    # Filter rows by confidence
    new_rows = result.get("new_rows", [])
    
    # Example: Only keep rows with amount > 100
    filtered_rows = [
        row for row in new_rows
        if row.get("WRBTR") and float(row["WRBTR"]) > 100
    ]
    
    print(f"Original rows: {len(new_rows)}")
    print(f"Filtered rows (amount > 100): {len(filtered_rows)}")
    
    # Example: Group by cost center
    cost_centers = {}
    for row in new_rows:
        cc = row.get("KOSTL", "Unknown")
        if cc not in cost_centers:
            cost_centers[cc] = []
        cost_centers[cc].append(row)
    
    print(f"\nRows by Cost Center:")
    for cc, rows in cost_centers.items():
        total = sum(float(r.get("WRBTR", 0)) for r in rows)
        print(f"  {cc}: {len(rows)} rows, Total: {total:.2f}")
    
    return filtered_rows


# ============================================================================
# Example 5: Accessing Raw and SAP JSON
# ============================================================================

def example_5_json_access():
    """Access and analyze raw and SAP JSON outputs"""
    print("\n" + "=" * 60)
    print("Example 5: JSON Access and Analysis")
    print("=" * 60)
    
    orchestrator = OrchestratorAgent()
    
    result = orchestrator.execute({
        "pdf_path": "POC_1.pdf",
        "output_dir": "output"
    })
    
    if result["status"] != "success":
        print("❌ Processing failed")
        return
    
    # Load raw JSON
    with open(result["raw_json_path"], "r", encoding="utf-8") as f:
        raw_json = json.load(f)
    
    # Load SAP JSON
    with open(result["sap_json_path"], "r", encoding="utf-8") as f:
        sap_json = json.load(f)
    
    print("\n📄 Raw JSON Analysis:")
    print(f"  Invoices: {len(raw_json.get('invoices', []))}")
    
    for idx, invoice in enumerate(raw_json.get("invoices", []), 1):
        print(f"\n  Invoice {idx}:")
        print(f"    Number: {invoice.get('invoice_number')}")
        print(f"    Date: {invoice.get('invoice_date')}")
        print(f"    Total: {invoice.get('total_amount')} {invoice.get('currency')}")
        print(f"    Line Items: {len(invoice.get('line_items', []))}")
    
    print("\n🔄 SAP JSON Analysis:")
    print(f"  Invoices: {len(sap_json.get('invoices', []))}")
    
    for idx, invoice in enumerate(sap_json.get("invoices", []), 1):
        header = invoice.get("header", {})
        line_items = invoice.get("line_items", [])
        
        print(f"\n  Invoice {idx}:")
        print(f"    BELNR: {header.get('BELNR')}")
        print(f"    BLDAT: {header.get('BLDAT')}")
        print(f"    WAERS: {header.get('WAERS')}")
        print(f"    Line Items: {len(line_items)}")
        
        total_amount = sum(float(item.get("WRBTR", 0)) for item in line_items)
        print(f"    Total Amount: {total_amount:.2f}")
    
    return raw_json, sap_json


# ============================================================================
# Example 6: Error Handling and Recovery
# ============================================================================

def example_6_error_handling():
    """Demonstrate error handling"""
    print("\n" + "=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)
    
    orchestrator = OrchestratorAgent()
    
    # Test with non-existent file
    print("\n[Test 1] Non-existent file:")
    result = orchestrator.execute({
        "pdf_path": "non_existent.pdf",
        "output_dir": "output"
    })
    
    if result.get("status") == "failed":
        print(f"  ✅ Error caught: {result.get('error')}")
    
    # Test with valid file
    print("\n[Test 2] Valid file:")
    result = orchestrator.execute({
        "pdf_path": "POC_1.pdf",
        "output_dir": "output"
    })
    
    if result.get("status") == "success":
        print(f"  ✅ Success - Confidence: {result['confidence_score']:.1%}")
        
        # Check for issues
        issues = result.get("issues", [])
        warnings = result.get("warnings", [])
        
        if issues:
            print(f"\n  ⚠️  Issues found ({len(issues)}):")
            for issue in issues[:3]:
                print(f"    - {issue}")
        
        if warnings:
            print(f"\n  ⚡ Warnings found ({len(warnings)}):")
            for warning in warnings[:3]:
                print(f"    - {warning}")


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SAP Invoice Processing System - Example Usage")
    print("=" * 60)
    
    # Run examples
    try:
        # Example 1: Simple processing
        example_1_simple_processing()
        
        # Example 2: Manual agent control
        # example_2_manual_agents()
        
        # Example 3: Batch processing
        # example_3_batch_processing()
        
        # Example 4: Custom filtering
        # example_4_custom_filtering()
        
        # Example 5: JSON access
        # example_5_json_access()
        
        # Example 6: Error handling
        # example_6_error_handling()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nUncomment other examples in __main__ to try them.")
