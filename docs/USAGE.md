# Usage Guide

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Groq credentials in `.env`:
```
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile
```

## Running the Application

### Option 1: Streamlit UI (Recommended)

```bash
streamlit run app.py
```

Then:
1. Upload a PDF invoice
2. Configure base Excel path (optional)
3. Click "Process Invoice"
4. View results and download outputs

### Option 2: Python Script

```python
from agents.orchestrator import OrchestratorAgent

orchestrator = OrchestratorAgent()

result = orchestrator.execute({
    "pdf_path": "invoice.pdf",
    "base_excel_path": "consolidated_acss_invoices_sample_output.xlsx",
    "output_dir": "output"
})

print(result)
```

### Option 3: Test Script

```bash
python test_system.py
```

## Output Files

After processing, you'll get:

1. **Raw JSON** (`raw_invoice_TIMESTAMP.json`)
   - Lossless extraction of all invoice data
   - Verbose, unstructured format
   - For debugging and audit

2. **SAP JSON** (`sap_invoice_TIMESTAMP.json`)
   - Normalized to SAP schema
   - Strict, minimal format
   - Single source of truth

3. **Excel File** (`invoice_output_TIMESTAMP.xlsx`)
   - SAP-formatted rows
   - Ready for import
   - Appended to base file if provided

4. **Confidence Report** (`confidence_report_TIMESTAMP.json`)
   - Validation results
   - Confidence score
   - Issues and warnings

## Understanding the Output

### Confidence Score

- **0.9 - 1.0**: Excellent - All required fields present and valid
- **0.7 - 0.9**: Good - Minor issues or warnings
- **0.5 - 0.7**: Fair - Some required fields missing
- **< 0.5**: Poor - Major issues, manual review needed

### Issues vs Warnings

- **Issues**: Missing required fields, invalid data types
- **Warnings**: Missing optional fields, minor inconsistencies

## Excel Schema

The output Excel follows this SAP schema:

| Column | Description | Source |
|--------|-------------|--------|
| BELNR | Document Number | PDF |
| BUDAT | Posting Date | Inferred |
| BLDAT | Document Date | PDF |
| BLART | Document Type | Default: "KR" |
| BUKRS | Company Code | PDF/Inferred |
| WAERS | Currency | PDF |
| WRBTR | Amount | PDF |
| SGTXT | Description | PDF |
| ... | ... | ... |

## Customization

### Changing Default Values

Edit `config/sap_schema.py`:

```python
DEFAULT_VALUES = {
    "BLART": "KR",  # Change document type
    "BSCHL": "31",  # Change posting key
    ...
}
```

### Adding Custom Fields

1. Add to `SAP_COLUMNS` in `config/sap_schema.py`
2. Update LLM normalization prompt in `agents/llm_agent.py`
3. Update Excel mapping in `agents/excel_agent.py`

### Adjusting LLM Behavior

Edit prompts in `agents/llm_agent.py`:
- `_detect_invoices()`: Detection logic
- `_extract_invoices()`: Extraction instructions
- `_normalize_to_sap()`: Normalization rules

## Troubleshooting

### Low Confidence Score

- Check if PDF is text-based (not scanned image)
- Verify invoice has standard structure
- Review issues in confidence report

### Missing Fields

- Check if field is in PDF
- Verify field mapping in normalization prompt
- Add field to `PDF_PRESENT_FIELDS` if applicable

### LLM Errors

- Check Groq credentials
- Verify API quota
- Check network connectivity

### Excel Generation Fails

- Verify base Excel file exists
- Check write permissions on output directory
- Ensure SAP schema matches

## Best Practices

1. **Always review confidence report** before using output
2. **Keep raw JSON** for audit trail
3. **Test with sample invoices** before production use
4. **Monitor LLM costs** - each invoice uses ~2-3 API calls
5. **Validate output** against source PDF manually for first few invoices
