# PDF Agent with AWS Textract Fallback

## Overview

The PDF Agent now includes intelligent fallback capability using AWS Textract for processing scanned or image-based PDFs that cannot be handled effectively by PDFPlumber.

## How It Works

### Primary Processing (PDFPlumber)
- Fast text extraction for text-based PDFs
- Table detection and extraction
- Minimal resource usage

### Fallback Processing (AWS Textract)
- Automatic activation when:
  - PDFPlumber extracts less than 100 characters (likely scanned PDF)
  - PDFPlumber fails completely with an exception
- OCR capability for scanned documents
- Advanced form and table detection
- Key-value pair extraction

## Processing Flow

```
PDF Input
    ↓
PDFPlumber Extraction
    ↓
Content Check (< 100 chars?)
    ↓ YES
AWS Textract Fallback
    ↓
Structured Output
```

## AWS Textract Features

### Key-Value Pairs
- Automatically detects form fields
- Extracts labels and their corresponding values
- Cleans and formats key names

### Table Extraction
- Maintains table structure with rows and columns
- Handles complex table layouts
- Preserves cell relationships

### Text Extraction
- OCR for scanned documents
- Line-by-line text extraction
- Excludes text already captured in forms/tables

## Configuration

### Environment Variables
```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

### Dependencies
- `boto3` - AWS SDK
- `PyMuPDF` - PDF to image conversion
- `Pillow` - Image processing

## Output Format

The agent maintains consistent output format regardless of processing method:

```python
{
    "raw_text": str,           # Combined text from all pages
    "pages": List[str],        # Text per page
    "tables": List[List[List[str]]], # Extracted tables
    "metadata": {
        "num_pages": int,
        "num_tables": int,
        "processing_method": str,  # "PDFPlumber" or "AWS Textract"
        "textract_details": dict   # Additional Textract data (if used)
    },
    "status": "success"
}
```

## Benefits

1. **Robust Processing**: Handles both text-based and scanned PDFs
2. **Automatic Fallback**: No manual intervention required
3. **Consistent Interface**: Same API regardless of processing method
4. **Enhanced Extraction**: Better structure detection with Textract
5. **Cost Optimization**: Uses free PDFPlumber first, Textract only when needed

## Usage Example

```python
from agents.pdf_agent import PDFAgent

# Initialize agent
pdf_agent = PDFAgent()

# Process any PDF (text-based or scanned)
result = pdf_agent.execute({"pdf_path": "document.pdf"})

if result["status"] == "success":
    print(f"Method: {result['metadata']['processing_method']}")
    print(f"Pages: {result['metadata']['num_pages']}")
    print(f"Tables: {result['metadata']['num_tables']}")
```

## Error Handling

- Graceful fallback when PDFPlumber fails
- Detailed logging for troubleshooting
- Fallback to simple text detection if forms/tables fail
- Maintains page structure even with partial failures

## Cost Considerations

- PDFPlumber: Free, local processing
- AWS Textract: Pay-per-page processed
- Automatic optimization uses free method first
- Textract only for scanned/problematic PDFs