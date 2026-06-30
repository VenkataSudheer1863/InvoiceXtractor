# System Flow Diagram

## Complete Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                             │
│                                                                      │
│  ┌──────────────┐         ┌──────────────┐      ┌──────────────┐  │
│  │  Streamlit   │   OR    │  Command     │  OR  │  Python      │  │
│  │  Web UI      │         │  Line        │      │  Script      │  │
│  │  (app.py)    │         │(test_system) │      │(example_usage)│  │
│  └──────┬───────┘         └──────┬───────┘      └──────┬───────┘  │
│         │                        │                     │           │
│         └────────────────────────┼─────────────────────┘           │
│                                  │                                 │
└──────────────────────────────────┼─────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR AGENT                              │
│                   (agents/orchestrator.py)                           │
│                                                                      │
│  Responsibilities:                                                   │
│  • Coordinate all agents                                            │
│  • Manage workflow state                                            │
│  • Save intermediate outputs                                        │
│  • Handle errors gracefully                                         │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
        ┌───────────────┐  ┌──────────────┐  ┌──────────────┐
        │   STEP 1      │  │   STEP 2     │  │   STEP 3     │
        │  PDF Agent    │  │  LLM Agent   │  │ Validation   │
        │               │  │              │  │   Agent      │
        └───────┬───────┘  └──────┬───────┘  └──────┬───────┘
                │                 │                 │
                ▼                 ▼                 ▼
        ┌───────────────┐  ┌──────────────┐  ┌──────────────┐
        │ Raw Text      │  │ Raw JSON     │  │ Confidence   │
        │ + Tables      │  │ + SAP JSON   │  │ Report       │
        └───────────────┘  └──────────────┘  └──────────────┘
                                   │
                                   ▼
                          ┌──────────────┐
                          │   STEP 4     │
                          │ Excel Agent  │
                          │              │
                          └──────┬───────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │ SAP Excel    │
                          │ File         │
                          └──────────────┘
```

## Detailed Agent Flow

### 1. PDF Agent Flow

```
Input: PDF File Path
    │
    ├─► Open PDF with pdfplumber
    │
    ├─► For each page:
    │   ├─► Extract text
    │   └─► Extract tables
    │
    └─► Output:
        ├─► raw_text (all pages combined)
        ├─► pages (list of page texts)
        ├─► tables (list of table data)
        └─► metadata (page count, etc.)
```

### 2. LLM Agent Flow

```
Input: Raw Text + Tables
    │
    ├─► PHASE 1: Detection
    │   ├─► LLM Call: "How many invoices?"
    │   └─► Output: num_invoices
    │
    ├─► PHASE 2: Extraction
    │   ├─► LLM Call: "Extract all invoice data"
    │   └─► Output: Raw JSON (lossless)
    │       {
    │         "invoices": [
    │           {
    │             "invoice_number": "...",
    │             "invoice_date": "...",
    │             "line_items": [...],
    │             ...
    │           }
    │         ]
    │       }
    │
    └─► PHASE 3: Normalization
        ├─► LLM Call: "Normalize to SAP schema"
        └─► Output: SAP JSON (schema-aligned)
            {
              "invoices": [
                {
                  "header": {
                    "BELNR": "...",
                    "BLDAT": "...",
                    ...
                  },
                  "line_items": [
                    {
                      "WRBTR": 100.00,
                      "SGTXT": "...",
                      ...
                    }
                  ]
                }
              ]
            }
```

### 3. Validation Agent Flow

```
Input: SAP JSON + Raw JSON
    │
    ├─► Check Required Fields
    │   ├─► BELNR present?
    │   ├─► BLDAT present?
    │   └─► WAERS present?
    │
    ├─► Validate Data Types
    │   ├─► Amounts are numeric?
    │   ├─► Dates are ISO format?
    │   └─► Currency is valid?
    │
    ├─► Calculate Confidence Score
    │   ├─► Field completeness: 0-1
    │   ├─► Data validity: 0-1
    │   └─► Adjust for issues/warnings
    │
    └─► Output:
        ├─► confidence_score (0-1)
        ├─► validation_report
        ├─► issues (list)
        └─► warnings (list)
```

### 4. Excel Agent Flow

```
Input: SAP JSON + Base Excel (optional)
    │
    ├─► For each invoice:
    │   ├─► Get header fields
    │   └─► For each line item:
    │       ├─► Merge header + line item
    │       ├─► Map to SAP columns
    │       └─► Apply default values
    │
    ├─► Create DataFrame
    │   ├─► All 35 SAP columns
    │   └─► N rows (one per line item)
    │
    ├─► Load base Excel (if exists)
    │   └─► Append new rows
    │
    └─► Output:
        ├─► Excel file (.xlsx)
        ├─► new_rows (list of dicts)
        └─► num_rows_added
```

## Data Transformation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         PDF DOCUMENT                             │
│                                                                  │
│  Invoice No: INV-2024-001                                       │
│  Date: 15/03/2024                                               │
│  Item 1: Product A - $100.00                                    │
│  Item 2: Product B - $200.00                                    │
│  Tax: $30.00                                                    │
│  Total: $330.00                                                 │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼ [PDF Agent]
┌─────────────────────────────────────────────────────────────────┐
│                         RAW TEXT                                 │
│                                                                  │
│  "Invoice No: INV-2024-001\nDate: 15/03/2024\n..."             │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼ [LLM Agent - Extraction]
┌─────────────────────────────────────────────────────────────────┐
│                         RAW JSON                                 │
│                                                                  │
│  {                                                              │
│    "invoices": [{                                               │
│      "invoice_number": "INV-2024-001",                         │
│      "invoice_date": "2024-03-15",                             │
│      "line_items": [                                            │
│        {"description": "Product A", "amount": 100.00},         │
│        {"description": "Product B", "amount": 200.00}          │
│      ],                                                         │
│      "total_tax": 30.00,                                       │
│      "total_amount": 330.00                                    │
│    }]                                                           │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼ [LLM Agent - Normalization]
┌─────────────────────────────────────────────────────────────────┐
│                         SAP JSON                                 │
│                                                                  │
│  {                                                              │
│    "invoices": [{                                               │
│      "header": {                                                │
│        "BELNR": "INV-2024-001",                                │
│        "BLDAT": "2024-03-15",                                  │
│        "WAERS": "USD",                                         │
│        "BLART": "KR"                                           │
│      },                                                         │
│      "line_items": [                                            │
│        {                                                        │
│          "SGTXT": "Product A",                                 │
│          "WRBTR": 100.00,                                      │
│          "BSCHL": "31",                                        │
│          ...                                                    │
│        },                                                       │
│        {                                                        │
│          "SGTXT": "Product B",                                 │
│          "WRBTR": 200.00,                                      │
│          "BSCHL": "31",                                        │
│          ...                                                    │
│        }                                                        │
│      ]                                                          │
│    }]                                                           │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼ [Excel Agent]
┌─────────────────────────────────────────────────────────────────┐
│                         SAP EXCEL                                │
│                                                                  │
│  BELNR        BLDAT      WAERS  WRBTR   SGTXT      BSCHL ...   │
│  INV-2024-001 2024-03-15 USD    100.00  Product A  31    ...   │
│  INV-2024-001 2024-03-15 USD    200.00  Product B  31    ...   │
└─────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      Any Agent Fails                             │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Agent Returns Error                            │
│                   {"status": "failed", "error": "..."}          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              Orchestrator Catches Error                          │
│              • Logs error                                        │
│              • Saves partial results                             │
│              • Returns error to user                             │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   User Sees Error                                │
│                   • In UI: Red error message                     │
│                   • In CLI: Error output                         │
│                   • In Script: Exception or error dict           │
└─────────────────────────────────────────────────────────────────┘
```

## Confidence Scoring Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   Validation Agent                               │
└─────────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Check        │   │ Validate     │   │ Count        │
│ Required     │   │ Data Types   │   │ Issues &     │
│ Fields       │   │ & Formats    │   │ Warnings     │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Calculate Score       │
              │                       │
              │ Base = Field Coverage │
              │ × 0.7 if issues       │
              │ × 0.9 if warnings     │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Confidence Score      │
              │                       │
              │ 0.9-1.0: Excellent    │
              │ 0.7-0.9: Good         │
              │ 0.5-0.7: Fair         │
              │ <0.5:    Poor         │
              └───────────────────────┘
```

## Multi-Invoice Handling

```
┌─────────────────────────────────────────────────────────────────┐
│              PDF with Multiple Invoices                          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼ [LLM Detection]
┌─────────────────────────────────────────────────────────────────┐
│              "3 invoices detected"                               │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼ [LLM Extraction]
┌─────────────────────────────────────────────────────────────────┐
│  {                                                              │
│    "invoices": [                                                │
│      { invoice 1 data },                                        │
│      { invoice 2 data },                                        │
│      { invoice 3 data }                                         │
│    ]                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼ [LLM Normalization]
┌─────────────────────────────────────────────────────────────────┐
│  {                                                              │
│    "invoices": [                                                │
│      { header: {...}, line_items: [3 items] },                 │
│      { header: {...}, line_items: [5 items] },                 │
│      { header: {...}, line_items: [2 items] }                  │
│    ]                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼ [Excel Generation]
┌─────────────────────────────────────────────────────────────────┐
│              Excel with 10 rows (3+5+2)                         │
│              All invoices in single file                        │
└─────────────────────────────────────────────────────────────────┘
```

## File Output Structure

```
output/
├── raw_invoice_20260203_143022.json
│   └─► Lossless extraction
│       • All invoice data
│       • Verbose format
│       • For debugging
│
├── sap_invoice_20260203_143022.json
│   └─► SAP-normalized
│       • Strict schema
│       • Minimal format
│       • Source of truth
│
├── invoice_output_20260203_143022.xlsx
│   └─► Final Excel
│       • 35 SAP columns
│       • N rows (line items)
│       • Ready for import
│
└── confidence_report_20260203_143022.json
    └─► Validation results
        • Confidence score
        • Issues list
        • Warnings list
        • Field coverage
```

---

**This flow ensures:**
- ✅ Lossless data extraction
- ✅ Semantic normalization
- ✅ Schema compliance
- ✅ Quality validation
- ✅ Audit trail
- ✅ Error handling
