# SAP Accounting Logic for Invoice Processing

## Understanding the Double-Entry System

SAP uses double-entry bookkeeping. For vendor invoices, you need:

### Line Items (BSCHL = 40)
- **Debit postings** to expense/GL accounts
- Each individual invoice line (Certificate of Origin, Service Charges, etc.)
- HKONT = K0551 (or specific GL account)
- These represent what you purchased/received

### Total Line (BSCHL = 31)
- **Credit posting** to vendor account
- One line per invoice with the total amount
- HKONT = 5373979 (vendor account)
- This represents what you owe the vendor

## Example

**Invoice INV1559104:**
- Line 1: Base Fare - 2,000 AED
- Line 2: Airport Tax - 540 AED
- Line 3: Corp Transaction Fee - 157 AED
- **Total: 2,697 AED**

**SAP Output (4 rows):**
1. BSCHL=40, HKONT=K0551, WRBTR=2000, SGTXT="Base Fare"
2. BSCHL=40, HKONT=K0551, WRBTR=540, SGTXT="Airport Tax"
3. BSCHL=40, HKONT=K0551, WRBTR=157, SGTXT="Corp Transaction Fee"
4. **BSCHL=31, HKONT=5373979, WRBTR=2697, SGTXT="Total Invoice"**

## Default SAP Codes

These are used when values are not found in the PDF:

| Field | Default | Description |
|-------|---------|-------------|
| BLART | KR | Document Type (Vendor Invoice) |
| BUKRS | 013 | Company Code |
| BSCHL | 40 | Posting Key for line items (debit) |
| BSCHL | 31 | Posting Key for total line (credit) |
| HKONT | K0551 | GL Account for line items |
| HKONT | 5373979 | GL Account for total (vendor account) |
| MWSKZ | U4 | Tax Code for 0% tax |
| MWSKZ | V1 | Tax Code for 5% tax |
| MEINS | each | Unit of Measure |

## Tax Code Inference

- **0% tax** → MWSKZ = U4
- **5% tax** → MWSKZ = V1

## Field Extraction Priority

1. **Extract from PDF** (if present)
2. **Infer from context** (e.g., tax codes from tax rates)
3. **Use defaults** (as specified above)
