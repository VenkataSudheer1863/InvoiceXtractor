# Continental InvoiceXtractor — Setup & Run Guide

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | |
| Tesseract OCR | 5.x | For image-based PDF fallback |
| AWS account | — | For Textract OCR (optional, needed for non-standard PDFs) |
| Groq API key | — | Free at https://console.groq.com |

## 1. Install Dependencies

```bash
cd "2.Continental_InvoiceXtractor"
pip install -r requirements.txt
```

**Tesseract (Windows):**
```powershell
winget install UB-Mannheim.TesseractOCR
```

## 2. Configure Environment

```bash
cp .env .env.bak
```

Edit `.env`:

```env
GROQ_API_KEY=gsk_...                  # Your Groq API key
GROQ_MODEL=llama-3.3-70b-versatile

# AWS Textract (optional — only needed for image-heavy PDFs)
AWS_ACCESS_KEY_ID=your-key-id
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

> If you don't have AWS credentials, the system falls back to `pdfplumber` for text extraction.
> Textract is only invoked when direct text extraction yields fewer than 50 characters.

## 3. Run the Application

**Streamlit UI:**
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

## 4. Verify Installation

```bash
python tests/verify_installation.py
```

This checks that all packages are installed and `GROQ_API_KEY` is present.

## 5. Run Tests

```bash
python test_system.py
```

## 6. Usage

1. Open the UI and upload one or more PDF invoices
2. The system extracts line items, supplier info, dates, and totals
3. Validates extracted data against the SAP schema
4. Exports a structured Excel file ready for SAP upload

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| `AuthenticationError: GROQ_API_KEY` | Set `GROQ_API_KEY` in `.env` |
| `pdfplumber` extracts empty text | PDF is image-based — add AWS Textract credentials |
| `FileNotFoundError: tesseract` | Install Tesseract OCR and add to PATH |
| Excel export blank | Check `output/` directory permissions |
