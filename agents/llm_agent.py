"""LLM Agent for Invoice Detection, Extraction, and Normalization"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from groq import Groq
from dotenv import load_dotenv
from .base_agent import BaseAgent
from config.sap_schema import SAP_FIELD_DESCRIPTIONS, PDF_PRESENT_FIELDS, INFERRED_FIELDS

load_dotenv()

class LLMAgent(BaseAgent):
    """Agent responsible for LLM-based extraction and normalization"""

    def __init__(self):
        super().__init__("LLMAgent")
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution: detect, extract, and normalize invoices

        Args:
            input_data: {"raw_text": str, "tables": List}

        Returns:
            {
                "raw_json": Dict,
                "sap_json": Dict,
                "num_invoices": int
            }
        """
        raw_text = input_data.get("raw_text", "")
        tables = input_data.get("tables", [])

        # Step 1: Detect number of invoices
        num_invoices = self._detect_invoices(raw_text)
        self.log_info(f"Detected {num_invoices} invoice(s)")

        # Step 2: Extract raw invoice data
        raw_json = self._extract_invoices(raw_text, tables, num_invoices)

        # Step 3: Normalize to SAP format
        sap_json = self._normalize_to_sap(raw_json)

        return {
            "raw_json": raw_json,
            "sap_json": sap_json,
            "num_invoices": num_invoices,
            "status": "success"
        }

    def _chat(self, system: str, user: str) -> str:
        """Send a chat request to Groq and return the content string."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=8192,
        )
        return response.choices[0].message.content

    def _detect_invoices(self, text: str) -> int:
        """Detect number of invoices in the PDF"""
        sample_text = text[:5000]

        prompt = f"""Analyze the following text and determine how many separate invoices are present.

IMPORTANT:
- If this is a STATEMENT (e.g., American Express statement, bank statement), count each unique invoice number referenced in the transaction details
- If this is a SINGLE INVOICE, return 1
- Do NOT count statement summary sections as invoices
- Look for invoice numbers, transaction references, or ticket numbers to count invoices
- For statements, look for patterns like "Invoice Number", "Invoice 001...", "Subtotal 001..." to count

Text:
{sample_text}

Response format:
{{"num_invoices": <number>, "document_type": "statement" or "invoice"}}"""

        try:
            content = self._chat(
                "You are an invoice detection expert. Return only valid JSON.",
                prompt
            )
            result = json.loads(content)
            return result.get("num_invoices", 1)

        except Exception as e:
            self.log_warning(f"Detection failed: {e}. Assuming 1 invoice.")
            return 1

    def _extract_invoices(self, text: str, tables: List, num_invoices: int) -> Dict[str, Any]:
        """Extract all invoice data into raw JSON"""

        if len(text) > 50000 or num_invoices > 10:
            self.log_info(f"Large document detected ({len(text)} chars, {num_invoices} invoices). Using chunked extraction.")
            return self._extract_invoices_chunked(text, tables, num_invoices)

        return self._extract_invoices_single(text, tables, num_invoices)

    def _extract_invoices_single(self, text: str, tables: List, num_invoices: int) -> Dict[str, Any]:
        """Extract invoices from a single document in one pass"""

        prompt = f"""Extract ALL invoice information from the text below. Be comprehensive and lossless.

IMPORTANT - Document Type Detection:
1. If this is a STATEMENT (e.g., American Express statement, bank statement):
   - Extract each referenced invoice number as a SEPARATE invoice
   - Do NOT treat statement summary fields (Previous Balance, New Remittance, Total Balance Due, etc.) as line items
   - Look for transaction details sections that list individual invoices

2. If this is a SINGLE INVOICE:
   - Extract all line items from that invoice
   - Include the total line as the last line item

CRITICAL - Granularity:
- Extract EVERY individual charge/line item separately, do NOT aggregate or summarize
- Each charge, fee, surcharge, tax should be its own line item
- Only the final total/subtotal should be marked as a total line

Extract the following information for each invoice:
- Invoice number, date, due date
- Vendor/supplier information
- Customer/buyer information
- Line items with: description, quantity, unit, unit price, amount, tax
- Subtotal, tax amount, total amount
- Payment terms, currency
- Any reference numbers, cost centers, project codes, GL accounts, company codes

Text:
{text}

Tables (if any):
{json.dumps(tables[:5], indent=2) if tables else "None"}

Return a JSON object with this structure:
{{
  "invoices": [
    {{
      "invoice_number": "...",
      "invoice_date": "YYYY-MM-DD",
      "due_date": "YYYY-MM-DD",
      "vendor": {{}},
      "customer": {{}},
      "currency": "...",
      "line_items": [
        {{
          "description": "...",
          "quantity": 0,
          "unit": "...",
          "unit_price": 0,
          "amount": 0,
          "tax_amount": 0,
          "tax_rate": 0,
          "cost_center": "...",
          "gl_account": "..."
        }}
      ],
      "subtotal": 0,
      "total_tax": 0,
      "total_amount": 0,
      "payment_terms": "...",
      "reference_numbers": {{}},
      "additional_fields": {{}}
    }}
  ],
  "_metadata": {{
    "extraction_timestamp": "...",
    "num_invoices": {num_invoices}
  }}
}}

IMPORTANT:
- All dates must be in YYYY-MM-DD format
- All amounts must be numeric (not strings)
- Extract ALL information, even if not sure where it maps
- Do not hallucinate - only extract what's present
- Extract EVERY charge separately - do NOT combine or aggregate charges"""

        try:
            content = self._chat(
                "You are an expert invoice data extraction system. Return only valid JSON with all extracted information.",
                prompt
            )
            raw_json = json.loads(content)
            self.log_info("Raw extraction completed")
            return raw_json

        except Exception as e:
            self.log_error(f"Extraction failed: {e}")
            return {"invoices": [], "error": str(e)}

    def _extract_invoices_chunked(self, text: str, tables: List, num_invoices: int) -> Dict[str, Any]:
        """Extract invoices from large documents by processing in chunks"""

        import re

        invoice_pattern = r'(?:Invoice Number|Invoice\s+\d{6,}|Subtotal\s+\d{6,})'
        matches = list(re.finditer(invoice_pattern, text, re.IGNORECASE))

        if len(matches) < 2:
            self.log_info("No clear invoice boundaries found. Using character-based chunking.")
            return self._extract_by_char_chunks(text, tables, num_invoices)

        chunks = []
        chunk_size = 15000
        current_chunk = ""
        current_start = 0

        for match in matches:
            chunk_text = text[current_start:match.start()]

            if len(current_chunk) + len(chunk_text) > chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = chunk_text
            else:
                current_chunk += chunk_text

            current_start = match.start()

        if current_start < len(text):
            current_chunk += text[current_start:]
        if current_chunk:
            chunks.append(current_chunk)

        self.log_info(f"Split document into {len(chunks)} chunks")

        all_invoices = []
        for i, chunk in enumerate(chunks):
            self.log_info(f"Processing chunk {i+1}/{len(chunks)}")

            prompt = f"""Extract ALL invoice information from the following text chunk. This is part of a larger statement.

IMPORTANT:
- This is a STATEMENT with multiple invoices
- Extract each invoice number as a SEPARATE invoice
- Do NOT treat statement summary fields as line items
- Extract EVERY individual charge separately

Text chunk {i+1}/{len(chunks)}:
{chunk[:15000]}

Return JSON with this structure:
{{
  "invoices": [
    {{
      "invoice_number": "...",
      "invoice_date": "YYYY-MM-DD",
      "line_items": [
        {{"description": "...", "amount": 0}}
      ],
      "total_amount": 0
    }}
  ]
}}"""

            try:
                content = self._chat(
                    "You are an expert invoice data extraction system. Return only valid JSON.",
                    prompt
                )
                chunk_result = json.loads(content)
                chunk_invoices = chunk_result.get("invoices", [])
                all_invoices.extend(chunk_invoices)
                self.log_info(f"Extracted {len(chunk_invoices)} invoices from chunk {i+1}")

            except Exception as e:
                self.log_error(f"Chunk {i+1} extraction failed: {e}")
                continue

        self.log_info(f"Total invoices extracted: {len(all_invoices)}")

        return {
            "invoices": all_invoices,
            "_metadata": {
                "extraction_timestamp": datetime.now().isoformat(),
                "num_invoices": len(all_invoices),
                "chunks_processed": len(chunks)
            }
        }

    def _extract_by_char_chunks(self, text: str, tables: List, num_invoices: int) -> Dict[str, Any]:
        """Fallback: Extract by splitting text into fixed-size chunks"""
        chunk_size = 15000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

        self.log_info(f"Using character-based chunking: {len(chunks)} chunks")

        all_invoices = []
        for i, chunk in enumerate(chunks):
            self.log_info(f"Processing chunk {i+1}/{len(chunks)}")
            result = self._extract_invoices_single(chunk, [], 1)
            chunk_invoices = result.get("invoices", [])
            all_invoices.extend(chunk_invoices)

        return {
            "invoices": all_invoices,
            "_metadata": {
                "extraction_timestamp": datetime.now().isoformat(),
                "num_invoices": len(all_invoices)
            }
        }

    def _normalize_to_sap(self, raw_json: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw JSON to SAP schema"""

        invoices = raw_json.get("invoices", [])

        if len(invoices) > 10:
            self.log_info(f"Large batch detected ({len(invoices)} invoices). Using batched normalization.")
            return self._normalize_to_sap_batched(raw_json)

        return self._normalize_to_sap_single(raw_json)

    def _normalize_to_sap_single(self, raw_json: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw JSON to SAP schema in a single pass"""

        sap_schema_desc = "\n".join([f"- {k}: {v}" for k, v in SAP_FIELD_DESCRIPTIONS.items()])

        prompt = f"""Normalize the following raw invoice JSON to SAP format.

SAP Field Definitions:
{sap_schema_desc}

Raw Invoice Data:
{json.dumps(raw_json, indent=2)}

Normalization Rules:
1. Map each line item to a separate SAP record
2. Use ISO date format (YYYY-MM-DD) for all dates
3. All amounts must be numeric
4. BLART should be "KR" for vendor invoices
5. BSCHL should be "40" for individual line items (debit posting)
6. BSCHL should be "31" for the TOTAL/SUMMARY line (credit posting to vendor account)
7. Calculate "Tage" (payment days) as: (ZFBDT or due_date) - (BLDAT or invoice_date)
8. If BUDAT (posting date) is not present, use current date
9. Map currency to WAERS
10. Map invoice number to BELNR
11. Map invoice date to BLDAT
12. Map line item description to SGTXT and Artikel
13. Map amount to WRBTR and "Betrag in HW"
14. Map tax amount to Steuerbetrag
15. Map quantity to MENGE
16. Map unit to MEINS (default to "each" if not specified)
17. Map cost center to KOSTL (if present, else "")
18. Map GL account to HKONT (if present, default: K0551 for line items, 5373979 for total)
19. Map company code to BUKRS (default: "013")
20. Map tax code to MWSKZ (infer from tax rate: 0% = U4, 5% = V1)
21. CRITICAL: ALWAYS create a final line item for the TOTAL with BSCHL=31 and HKONT=5373979
22. CRITICAL: Do NOT aggregate or combine charges

Return JSON in this format:
{{
  "invoices": [
    {{
      "header": {{
        "BELNR": "...", "BUDAT": "YYYY-MM-DD", "BLDAT": "YYYY-MM-DD",
        "BLART": "KR", "BUKRS": "013", "WAERS": "...", "Kopftext": "..."
      }},
      "line_items": [
        {{
          "BSCHL": "40", "HKONT": "K0551", "BUKRS_BSEG": "013",
          "KOSTL": "", "AUFNR": "", "VBUND": "", "WRBTR": 0,
          "MWSKZ": "", "SGTXT": "", "ZUONR": "", "Projekt-Nr": "",
          "Steuerbetrag": 0, "MENGE": 0, "MEINS": "", "Bewegungsart": "",
          "BZDAT": "YYYY-MM-DD", "Betrag in HW": 0, "UMSKZ": "",
          "ZFBDT": "YYYY-MM-DD", "MWST": "", "Tage": 0, "Artikel": "",
          "Steuer": "", "WERK": "", "WWRPL": "", "WWRPM": "", "WWSPL": "", "WWOTL": ""
        }}
      ]
    }}
  ]
}}

CRITICAL: Return only valid JSON. No hallucinations. Use empty strings for missing optional fields."""

        try:
            content = self._chat(
                "You are an SAP invoice normalization expert. Return only valid JSON following the exact schema provided.",
                prompt
            )
            sap_json = json.loads(content)
            self.log_info("SAP normalization completed")
            return sap_json

        except Exception as e:
            self.log_error(f"Normalization failed: {e}")
            return {"invoices": [], "error": str(e)}

    def _normalize_to_sap_batched(self, raw_json: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize large batches of invoices in smaller groups"""

        invoices = raw_json.get("invoices", [])
        batch_size = 10

        all_sap_invoices = []
        total_batches = (len(invoices) + batch_size - 1) // batch_size

        for i in range(0, len(invoices), batch_size):
            batch = invoices[i:i+batch_size]
            batch_num = (i // batch_size) + 1

            self.log_info(f"Normalizing batch {batch_num}/{total_batches} ({len(batch)} invoices)")

            batch_raw_json = {
                "invoices": batch,
                "_metadata": raw_json.get("_metadata", {})
            }

            batch_sap = self._normalize_to_sap_single(batch_raw_json)
            batch_sap_invoices = batch_sap.get("invoices", [])
            all_sap_invoices.extend(batch_sap_invoices)

            self.log_info(f"Batch {batch_num} normalized: {len(batch_sap_invoices)} invoices")

        self.log_info(f"Total normalized: {len(all_sap_invoices)} invoices")

        return {
            "invoices": all_sap_invoices,
            "_metadata": {
                "normalization_timestamp": datetime.now().isoformat(),
                "total_invoices": len(all_sap_invoices),
                "batches_processed": total_batches
            }
        }
