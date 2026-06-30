# Complete Guide - SAP Invoice Processing System

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Architecture](#architecture)
5. [Customization](#customization)
6. [Troubleshooting](#troubleshooting)
7. [API Reference](#api-reference)

---

## 🚀 Quick Start

### 1. Verify Installation

```bash
python verify_installation.py
```

### 2. Run the System

```bash
streamlit run app.py
```

### 3. Process an Invoice

1. Upload PDF
2. Click "Process Invoice"
3. Download results

**Done!** See outputs in `output/` directory.

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Groq API access

### Step-by-Step Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify installation
python verify_installation.py

# 3. Check configuration
# Ensure .env has Groq credentials
```

### Dependencies

- **streamlit** - Web UI framework
- **pdfplumber** - PDF text extraction
- **groq** - Groq client
- **pandas** - Data manipulation
- **openpyxl** - Excel file handling
- **python-dotenv** - Environment configuration
- **pydantic** - Data validation

---

## 💻 Usage

### Option 1: Web UI (Recommended)

```bash
streamlit run app.py
```

**Features:**
- File upload interface
- Real-time processing status
- Results visualization
- Download buttons
- Confidence scoring
- Issues and warnings display

### Option 2: Command Line

```bash
python test_system.py
```

**Features:**
- Batch processing
- Terminal output
- Quick testing

### Option 3: Python Script

```python
from agents.orchestrator import OrchestratorAgent

orchestrator = OrchestratorAgent()

result = orchestrator.execute({
    "pdf_path": "invoice.pdf",
    "base_excel_path": "base.xlsx",  # optional
    "output_dir": "output"
})

print(f"Status: {result['status']}")
print(f"Confidence: {result['confidence_score']:.1%}")
print(f"Excel: {result['excel_path']}")
```

### Option 4: Advanced Usage

See `example_usage.py` for:
- Manual agent control
- Batch processing
- Custom filtering
- JSON access
- Error handling

---

## 🏗️ Architecture

### Multi-Agent System

```
Orchestrator Agent
    ├─► PDF Agent (Extract text)
    ├─► LLM Agent (Detect, Extract, Normalize)
    ├─► Validation Agent (Validate, Score)
    └─► Excel Agent (Generate Excel)
```

### Data Flow

```
PDF → Raw Text → Raw JSON → SAP JSON → Excel
                    ↓           ↓
                  Saved      Saved
```

### Agent Responsibilities

| Agent | Input | Output | Technology |
|-------|-------|--------|------------|
| **PDF Agent** | PDF file | Raw text + tables | pdfplumber |
| **LLM Agent** | Raw text | Raw JSON + SAP JSON | Groq |
| **Validation Agent** | SAP JSON | Confidence report | Python |
| **Excel Agent** | SAP JSON | Excel file | pandas, openpyxl |
| **Orchestrator** | PDF path | All outputs | Python |

### Key Design Principles

1. **Single Responsibility** - Each agent has one job
2. **JSON as Truth** - All data flows through JSON
3. **No Hardcoding** - Schema-driven design
4. **Audit Trail** - All outputs saved
5. **Graceful Degradation** - Errors handled independently

---

## 🎨 Customization

### 1. Add Custom SAP Fields

**File:** `config/sap_schema.py`

```python
# Add to column list
SAP_COLUMNS.append("MY_CUSTOM_FIELD")

# Add description
SAP_FIELD_DESCRIPTIONS["MY_CUSTOM_FIELD"] = "My field description"

# Add default value (optional)
DEFAULT_VALUES["MY_CUSTOM_FIELD"] = "default_value"
```

### 2. Modify LLM Prompts

**File:** `agents/llm_agent.py`

**Detection Prompt:**
```python
def _detect_invoices(self, text: str) -> int:
    prompt = f"""Your custom detection prompt..."""
```

**Extraction Prompt:**
```python
def _extract_invoices(self, text: str, tables: List, num_invoices: int) -> Dict:
    prompt = f"""Your custom extraction prompt..."""
```

**Normalization Prompt:**
```python
def _normalize_to_sap(self, raw_json: Dict) -> Dict:
    prompt = f"""Your custom normalization prompt..."""
```

### 3. Change Validation Rules

**File:** `agents/validation_agent.py`

```python
def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    # Add custom validation logic
    if custom_condition:
        issues.append("Custom validation failed")
    
    # Adjust confidence calculation
    confidence_score = custom_calculation()
```

### 4. Customize UI

**File:** `app.py`

```python
# Change layout
st.set_page_config(layout="wide")

# Add custom tabs
tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

# Add custom visualizations
st.plotly_chart(custom_chart)
```

### 5. Add New Agent

**Step 1:** Create agent file

```python
# agents/my_agent.py
from .base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("MyAgent")
    
    def execute(self, input_data):
        # Your logic here
        return {"status": "success"}
```

**Step 2:** Add to orchestrator

```python
# agents/orchestrator.py
from .my_agent import MyAgent

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("Orchestrator")
        self.my_agent = MyAgent()
    
    def execute(self, input_data):
        # Use your agent
        result = self.my_agent.execute(data)
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "Module not found" Error

**Problem:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
```

#### 2. "Groq error"

**Problem:** API credentials invalid or quota exceeded

**Solution:**
- Check `.env` file has correct credentials
- Verify API key is active
- Check Groq API quota

#### 3. "PDF extraction failed"

**Problem:** PDF is scanned image, not text-based

**Solution:**
- Ensure PDF has selectable text
- Use OCR tool to convert scanned PDF to text-based
- Try opening PDF manually to verify

#### 4. "Low confidence score"

**Problem:** Missing required fields or invalid data

**Solution:**
- Review confidence report for specific issues
- Check if invoice has standard structure
- Verify all required fields are present in PDF

#### 5. "Excel generation failed"

**Problem:** Base Excel file not found or invalid

**Solution:**
- Check base Excel path is correct
- Ensure file is not open in Excel
- Verify write permissions on output directory

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Intermediate Outputs

Review saved JSON files:
- `raw_invoice_*.json` - Check extraction
- `sap_invoice_*.json` - Check normalization
- `confidence_report_*.json` - Check validation

---

## 📖 API Reference

### OrchestratorAgent

**Main entry point for processing**

```python
orchestrator = OrchestratorAgent()

result = orchestrator.execute({
    "pdf_path": str,              # Required: Path to PDF file
    "base_excel_path": str,       # Optional: Base Excel to append to
    "output_dir": str             # Optional: Output directory (default: "output")
})

# Returns:
{
    "status": "success" | "failed",
    "raw_json_path": str,
    "sap_json_path": str,
    "excel_path": str,
    "confidence_report_path": str,
    "confidence_score": float,    # 0-1
    "validation_report": dict,
    "new_rows": list,
    "num_rows_added": int,
    "issues": list,
    "warnings": list
}
```

### PDFAgent

**Extract text from PDF**

```python
pdf_agent = PDFAgent()

result = pdf_agent.execute({
    "pdf_path": str               # Required: Path to PDF file
})

# Returns:
{
    "status": "success" | "failed",
    "raw_text": str,
    "pages": list,
    "tables": list,
    "metadata": dict
}
```

### LLMAgent

**AI-powered extraction and normalization**

```python
llm_agent = LLMAgent()

result = llm_agent.execute({
    "raw_text": str,              # Required: Raw text from PDF
    "tables": list                # Optional: Extracted tables
})

# Returns:
{
    "status": "success" | "failed",
    "raw_json": dict,
    "sap_json": dict,
    "num_invoices": int
}
```

### ValidationAgent

**Validate data and calculate confidence**

```python
validation_agent = ValidationAgent()

result = validation_agent.execute({
    "sap_json": dict,             # Required: SAP-normalized JSON
    "raw_json": dict              # Required: Raw extracted JSON
})

# Returns:
{
    "status": "success" | "failed",
    "confidence_score": float,    # 0-1
    "validation_report": dict,
    "issues": list,
    "warnings": list
}
```

### ExcelAgent

**Generate SAP-formatted Excel**

```python
excel_agent = ExcelAgent()

result = excel_agent.execute({
    "sap_json": dict,             # Required: SAP-normalized JSON
    "base_excel_path": str,       # Optional: Base Excel to append to
    "output_path": str            # Required: Output Excel path
})

# Returns:
{
    "status": "success" | "failed",
    "output_path": str,
    "num_rows_added": int,
    "new_rows": list
}
```

---

## 📊 SAP Schema Reference

### 35 SAP Fields

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| BELNR | String | Document Number | PDF |
| BUDAT | Date | Posting Date | Inferred |
| BLDAT | Date | Document Date | PDF |
| BLART | String | Document Type | Default: "KR" |
| BUKRS | String | Company Code | PDF/Inferred |
| WAERS | String | Currency | PDF |
| BSCHL | String | Posting Key | Default: "31" |
| HKONT | String | G/L Account | PDF/Inferred |
| BUKRS_BSEG | String | Company Code (line) | PDF/Inferred |
| KOSTL | String | Cost Center | PDF |
| AUFNR | String | Order Number | Optional |
| VBUND | String | Trading Partner | Optional |
| WRBTR | Number | Amount | PDF |
| MWSKZ | String | Tax Code | PDF/Inferred |
| SGTXT | String | Line Item Text | PDF |
| ZUONR | String | Assignment Number | PDF |
| Projekt-Nr | String | Project Number | Optional |
| Steuerbetrag | Number | Tax Amount | PDF |
| MENGE | Number | Quantity | PDF |
| MEINS | String | Unit | PDF |
| Bewegungsart | String | Movement Type | Optional |
| BZDAT | Date | Baseline Date | PDF |
| Betrag in HW | Number | Amount (local) | PDF |
| UMSKZ | String | Special G/L | Optional |
| ZFBDT | Date | Payment Terms Date | PDF |
| Kopftext | String | Header Text | PDF |
| MWST | String | VAT Indicator | PDF |
| Tage | Number | Payment Days | Calculated |
| Artikel | String | Article | PDF |
| Steuer | String | Tax Type | PDF |
| WERK | String | Plant | Optional |
| WWRPL | String | Work Center | Optional |
| WWRPM | String | Work Center Person | Optional |
| WWSPL | String | Storage Location | Optional |
| WWOTL | String | Work Order | Optional |

---

## 📚 Additional Resources

### Documentation Files

- **README.md** - Project overview
- **QUICKSTART.md** - 5-minute guide
- **PROJECT_STRUCTURE.md** - File structure
- **IMPLEMENTATION_SUMMARY.md** - What's been built
- **docs/ARCHITECTURE.md** - System design
- **docs/USAGE.md** - Detailed usage
- **docs/PROMPTS.md** - LLM prompts
- **docs/SYSTEM_FLOW.md** - Flow diagrams

### Example Files

- **test_system.py** - CLI testing
- **example_usage.py** - 6 usage examples
- **verify_installation.py** - Installation check

### Configuration Files

- **.env** - Groq credentials
- **config/sap_schema.py** - SAP schema definition
- **requirements.txt** - Python dependencies

---

## 🎯 Best Practices

### 1. Always Review Confidence Report

Check confidence score and issues before using output.

### 2. Keep Audit Trail

Save all JSON files for debugging and compliance.

### 3. Test with Samples First

Process sample invoices before production use.

### 4. Monitor LLM Costs

Each invoice uses ~3 API calls. Monitor usage.

### 5. Validate Output

Compare first few outputs with source PDFs manually.

### 6. Handle Errors Gracefully

Check `status` field in all results.

### 7. Use Batch Processing

Process multiple invoices efficiently with batch mode.

### 8. Customize for Your Needs

Adjust prompts and schema for your specific requirements.

---

## 🚀 Next Steps

1. **Run verification:** `python verify_installation.py`
2. **Start UI:** `streamlit run app.py`
3. **Process sample:** Upload `POC_1.pdf`
4. **Review output:** Check `output/` directory
5. **Customize:** Adjust schema and prompts as needed
6. **Scale:** Process multiple invoices in batch

---

## 📞 Support

For issues or questions:
1. Check this guide
2. Review documentation in `docs/`
3. Check example files
4. Review error messages in confidence report

---

**System Status: ✅ Production Ready**

Built with ❤️ using Multi-Agent Architecture
