# PDF Types Handled by the System

## Overview

The system intelligently handles two main types of documents:

## 1. Single Invoice PDFs (POC_1, POC_3, POC_4, POC_5, POC_6)

**Structure:**
```
Invoice Header
  - Invoice Number: INV1559104
  - Date: 2025-06-17
  - Customer Info
  
Line Items:
  1. Base Fare - 2,000 AED
  2. Airport Tax - 540 AED
  3. Corp Transaction Fee - 157 AED
  
Total: 2,697 AED
```

**System Output (4 rows):**
- 3 line items (BSCHL=40)
- 1 total line (BSCHL=31)

## 2. Statement PDFs (POC_2 - American Express Statement)

**Structure:**
```
Statement Header
  - Account Number: 3744XXXXXXX3193
  - Statement Date: 2025-06-28
  
Statement Summary (DO NOT EXTRACT AS LINE ITEMS):
  - Previous Balance: 164,307.51
  - New Remittance: 342,855.40
  - New Credits: 21,422.00
  - New Debits: 251,649.42
  - Total Balance Due: 51,679.53
  
Transaction Details (EXTRACT THESE):
  Invoice 001541181:
    - Ticket: 600 AED
    - Transaction Fee: 157 AED
    - Subtotal: 757 AED
    
  Invoice 001527190:
    - Ticket: 2,745 AED
    - Subtotal: 2,745 AED
    
  Invoice 000197069:
    - Refund: -560 AED
    - Subtotal: -560 AED
```

**System Output:**
- Multiple invoices, each with their own line items
- Each invoice gets its own set of rows with a total line

## Key Differences

| Aspect | Single Invoice | Statement |
|--------|---------------|-----------|
| Document Type | Invoice | Statement |
| Number of Invoices | 1 | Multiple (50+) |
| Summary Section | Part of invoice | Separate (ignore) |
| Extraction Logic | Extract all line items | Extract per-invoice details |

## Common Pitfalls to Avoid

### ❌ WRONG - Treating Statement Summary as Line Items
```
Row 1: Previous Balance - 164,307.51 (BSCHL=40)
Row 2: New Remittance - 342,855.40 (BSCHL=40)
Row 3: Total Balance Due - 51,679.53 (BSCHL=31)
```

### ✅ CORRECT - Extracting Individual Invoice Details
```
Invoice 001541181:
  Row 1: Ticket - 600 (BSCHL=40)
  Row 2: Fee - 157 (BSCHL=40)
  Row 3: Subtotal - 757 (BSCHL=31)

Invoice 001527190:
  Row 1: Ticket - 2,745 (BSCHL=40)
  Row 2: Subtotal - 2,745 (BSCHL=31)
```

## Detection Keywords

**Statement Indicators:**
- "Statement Date"
- "Account Number"
- "Previous Balance"
- "New Remittance"
- "Total Balance Due"
- "Transaction Details"
- Multiple invoice numbers in one document

**Single Invoice Indicators:**
- "Invoice Number" (singular)
- "Bill To"
- "Due Date"
- Line items with descriptions
- Single total at bottom

## LLM Instructions

The system instructs the LLM to:
1. Detect document type (statement vs invoice)
2. If statement: Extract each invoice separately from transaction details
3. If statement: Ignore summary fields (Previous Balance, Total Balance Due, etc.)
4. If invoice: Extract all line items + total
5. Always create total line with BSCHL=31 for each invoice
