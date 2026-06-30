# LLM Prompts Documentation

This document contains all LLM prompts used in the system for transparency and customization.

## 1. Invoice Detection Prompt

**Purpose**: Detect number of invoices in PDF

**Location**: `agents/llm_agent.py` → `_detect_invoices()`

**Prompt**:
```
Analyze the following text and determine how many separate invoices are present.
Return ONLY a JSON object with the count.

Text:
{text[:3000]}

Response format:
{"num_invoices": <number>}
```

**System Message**:
```
You are an invoice detection expert. Return only valid JSON.
```

**Parameters**:
- Temperature: 0 (deterministic)
- Response format: JSON object

---

## 2. Invoice Extraction Prompt

**Purpose**: Extract all invoice data into raw JSON (lossless)

**Location**: `agents/llm_agent.py` → `_extract_invoices()`

**Prompt**:
```
Extract ALL invoice information from the text below. Be comprehensive and lossless.

Extract the following information for each invoice:
- Invoice number, date, due date
- Vendor/supplier information
- Customer/buyer information  
- Line items with: description, quantity, unit, unit price, amount, tax
- Subtotal, tax amount, total amount
- Payment terms, currency
- Any reference numbers, cost centers, project codes
- Any other relevant fields

Text:
{text}

Tables (if any):
{tables}

Return a JSON object with this structure:
{
  "invoices": [
    {
      "invoice_number": "...",
      "invoice_date": "YYYY-MM-DD",
      "due_date": "YYYY-MM-DD",
      "vendor": {},
      "customer": {},
      "currency": "...",
      "line_items": [
        {
          "description": "...",
          "quantity": number,
          "unit": "...",
          "unit_price": number,
          "amount": number,
          "tax_amount": number,
          "tax_rate": number,
          "cost_center": "...",
          "gl_account": "..."
        }
      ],
      "subtotal": number,
      "total_tax": number,
      "total_amount": number,
      "payment_terms": "...",
      "reference_numbers": {},
      "additional_fields": {}
    }
  ],
  "_metadata": {
    "extraction_timestamp": "...",
    "num_invoices": {num_invoices}
  }
}

IMPORTANT:
- All dates must be in YYYY-MM-DD format
- All amounts must be numeric (not strings)
- Extract ALL information, even if not sure where it maps
- Do not hallucinate - only extract what's present
```

**System Message**:
```
You are an expert invoice data extraction system. Return only valid JSON with all extracted information.
```

**Parameters**:
- Temperature: 0 (deterministic)
- Response format: JSON object

---

## 3. SAP Normalization Prompt

**Purpose**: Normalize raw JSON to SAP schema

**Location**: `agents/llm_agent.py` → `_normalize_to_sap()`

**Prompt**:
```
Normalize the following raw invoice JSON to SAP format.

SAP Field Definitions:
- BELNR: Accounting Document Number
- BUDAT: Posting Date (YYYY-MM-DD)
- BLDAT: Document Date (YYYY-MM-DD)
- BLART: Document Type (e.g., KR for Vendor Invoice)
- BUKRS: Company Code
- WAERS: Currency Key (e.g., AED, USD)
- BSCHL: Posting Key
- HKONT: G/L Account Number
- BUKRS_BSEG: Company Code at line-item level
- KOSTL: Cost Center
- AUFNR: Internal Order Number
- VBUND: Trading Partner
- WRBTR: Amount in Document Currency (numeric)
- MWSKZ: Tax Code
- SGTXT: Line Item Text/Description
- ZUONR: Assignment Number
- Projekt-Nr: Project Number
- Steuerbetrag: Tax Amount (numeric)
- MENGE: Quantity (numeric)
- MEINS: Unit of Measure (e.g., EA, KG, HRS)
- Bewegungsart: Movement Type
- BZDAT: Baseline Date (YYYY-MM-DD)
- Betrag in HW: Amount in Local Currency (numeric)
- UMSKZ: Special G/L Indicator
- ZFBDT: Terms of Payment Date (YYYY-MM-DD)
- Kopftext: Document Header Text
- MWST: VAT/Tax Indicator
- Tage: Payment Days (numeric, calculated)
- Artikel: Article/Item Description
- Steuer: Tax Type
- WERK: Plant
- WWRPL: Work Center/Work Place
- WWRPM: Work Center Person/Machine
- WWSPL: Storage Location/Supply Area
- WWOTL: Work Order/Operation Location

Raw Invoice Data:
{raw_json}

Normalization Rules:
1. Map each line item to a separate SAP record
2. Use ISO date format (YYYY-MM-DD) for all dates
3. All amounts must be numeric
4. BLART should be "KR" for vendor invoices
5. BSCHL should be "31" for vendor invoice posting
6. Calculate "Tage" (payment days) as: (ZFBDT or due_date) - (BLDAT or invoice_date)
7. If BUDAT (posting date) is not present, use current date
8. Map currency to WAERS
9. Map invoice number to BELNR
10. Map invoice date to BLDAT
11. Map line item description to SGTXT and Artikel
12. Map amount to WRBTR and "Betrag in HW"
13. Map tax amount to Steuerbetrag
14. Map quantity to MENGE
15. Map unit to MEINS
16. Map cost center to KOSTL
17. Map reference to ZUONR
18. Map header text to Kopftext
19. Map tax info to MWST and Steuer
20. Leave optional fields empty if not present

Return JSON in this format:
{
  "invoices": [
    {
      "header": {
        "BELNR": "...",
        "BUDAT": "YYYY-MM-DD",
        "BLDAT": "YYYY-MM-DD",
        "BLART": "KR",
        "BUKRS": "...",
        "WAERS": "...",
        "Kopftext": "..."
      },
      "line_items": [
        {
          "BSCHL": "31",
          "HKONT": "...",
          "BUKRS_BSEG": "...",
          "KOSTL": "...",
          "AUFNR": "",
          "VBUND": "",
          "WRBTR": number,
          "MWSKZ": "...",
          "SGTXT": "...",
          "ZUONR": "...",
          "Projekt-Nr": "",
          "Steuerbetrag": number,
          "MENGE": number,
          "MEINS": "...",
          "Bewegungsart": "",
          "BZDAT": "YYYY-MM-DD",
          "Betrag in HW": number,
          "UMSKZ": "",
          "ZFBDT": "YYYY-MM-DD",
          "MWST": "...",
          "Tage": number,
          "Artikel": "...",
          "Steuer": "...",
          "WERK": "",
          "WWRPL": "",
          "WWRPM": "",
          "WWSPL": "",
          "WWOTL": ""
        }
      ]
    }
  ]
}

CRITICAL: Return only valid JSON. No hallucinations. Use empty strings for missing optional fields.
```

**System Message**:
```
You are an SAP invoice normalization expert. Return only valid JSON following the exact schema provided.
```

**Parameters**:
- Temperature: 0 (deterministic)
- Response format: JSON object

---

## Customization Guide

### Adjusting Extraction Depth

To extract more/less information, modify the extraction prompt:

**More detailed**:
```
- Extract vendor: name, address, tax ID, contact
- Extract customer: name, address, department
- Extract payment: bank details, IBAN, SWIFT
```

**Less detailed**:
```
- Extract only: invoice number, date, line items, total
```

### Adding Custom SAP Fields

1. Add field to SAP Field Definitions section
2. Add mapping rule to Normalization Rules
3. Update output JSON structure

### Handling Multiple Languages

Add to system message:
```
You are a multilingual invoice expert. Extract information regardless of language. 
Always output field names in English and dates in ISO format.
```

### Improving Accuracy

Add examples to prompt:
```
Example:
Input: "Invoice No: INV-2024-001"
Output: {"BELNR": "INV-2024-001"}

Input: "Date: 15/03/2024"
Output: {"BLDAT": "2024-03-15"}
```

### Cost Optimization

To reduce token usage:
- Limit text preview in detection (currently 3000 chars)
- Remove verbose instructions
- Use shorter field descriptions
- Reduce number of examples
