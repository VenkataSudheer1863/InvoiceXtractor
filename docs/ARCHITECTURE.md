# SAP Invoice Processing System - Architecture

## Table of Contents
1. [System Overview](#system-overview)
2. [Enhanced Multi-Agent Architecture](#enhanced-multi-agent-architecture)
3. [Component Details](#component-details)
4. [Data Flow Architecture](#data-flow-architecture)
5. [Processing Modes](#processing-modes)
6. [Integration Points](#integration-points)
7. [Error Handling Strategy](#error-handling-strategy)
8. [Extensibility Framework](#extensibility-framework)
9. [Deployment Architecture](#deployment-architecture)

---

## System Overview

The SAP Invoice Processing System is an enhanced multi-agent architecture designed to automatically process PDF invoices and convert them into SAP-formatted Excel files. The system has evolved to support diverse document types, batch processing, and intelligent file management while maintaining high reliability and audit capabilities.

### Core Capabilities
- **Hybrid PDF Processing**: Text-based PDFs (PDFPlumber) + Scanned PDFs (AWS Textract OCR)
- **Batch Processing**: Multiple PDF files processed simultaneously
- **Intelligent Excel Management**: Update existing files with automatic backups
- **Multi-Invoice Support**: Handle statements with multiple invoices per PDF
- **AI-Powered Extraction**: Groq for semantic understanding and normalization
- **Quality Assurance**: Comprehensive validation with confidence scoring
- **Complete Audit Trail**: Full processing history with intermediate outputs

---

## Enhanced Multi-Agent Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           User Interface Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │  Streamlit UI   │  │  Command Line   │  │  Python API     │            │
│  │  • Single PDF   │  │  • Batch Mode   │  │  • Programmatic │            │
│  │  • Batch Mode   │  │  • Automation   │  │  • Integration  │            │
│  │  • File Mgmt    │  │  • Testing      │  │  • Custom Logic │            │
│  └─────────┬───────┘  └─────────┬───────┘  └─────────┬───────┘            │
└───────────┼─────────────────────┼─────────────────────┼─────────────────────┘
            │                     │                     │
            └─────────────────────┼─────────────────────┘
                                  │
┌─────────────────────────────────┼─────────────────────────────────────────────┐
│                    Enhanced Orchestration Layer                             │
│                                 │                                            │
│         ┌───────────────────────▼─────────────────────────┐                 │
│         │        Enhanced Orchestrator Agent              │                 │
│         │  ┌─────────────────────────────────────────────┐ │                 │
│         │  │         Workflow Coordination               │ │                 │
│         │  │  • Single PDF Processing                    │ │                 │
│         │  │  • Batch PDF Processing                     │ │                 │
│         │  │  • Error Isolation & Recovery               │ │                 │
│         │  │  • Excel Update Management                  │ │                 │
│         │  │  • Result Aggregation                       │ │                 │
│         │  └─────────────────────────────────────────────┘ │                 │
│         └───────────────────┬─────────────────────────────┘                 │
└─────────────────────────────┼─────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼─────────────────────────────────────────────────┐
│                    Enhanced Processing Layer                                │
│                             │                                                │
│    ┌────────────────────────┼────────────────────────┐                      │
│    │                       │                        │                      │
│    ▼                       ▼                        ▼                      │
│ ┌─────────┐          ┌─────────┐              ┌─────────┐                  │
│ │Enhanced │          │   LLM   │              │Enhanced │                  │
│ │   PDF   │          │  Agent  │              │  Excel  │                  │
│ │  Agent  │          │         │              │  Agent  │                  │
│ │         │          │         │              │         │                  │
│ │ ┌─────┐ │          │ ┌─────┐ │              │ ┌─────┐ │                  │
│ │ │PDF  │ │          │ │Groq │ │              │ │File │ │                  │
│ │ │Plumb│ │          │ │LLaMA│ │              │ │Mgmt │ │                  │
│ │ │er   │ │          │ │3.3  │ │              │ │&Bkup│ │                  │
│ │ └─────┘ │          │ │70B  │ │              │ └─────┘ │                  │
│ │    ↓    │          │ └─────┘ │              │         │                  │
│ │ ┌─────┐ │          │         │              │         │                  │
│ │ │AWS  │ │          │ 3-Phase │              │ Update  │                  │
│ │ │Text │ │          │Process: │              │Existing │                  │
│ │ │ract │ │          │1.Detect │              │Files    │                  │
│ │ │OCR  │ │          │2.Extract│              │Create   │                  │
│ │ └─────┘ │          │3.Normal │              │Backups  │                  │
│ └─────────┘          └─────────┘              └─────────┘                  │
│     │                     │                        │                      │
│     ▼                     ▼                        ▼                      │
│ Raw Text              Raw JSON                Excel File                  │
│ +OCR Data             SAP JSON                +Backups                    │
│                           │                                               │
│                           ▼                                               │
│                   ┌─────────────┐                                        │
│                   │ Validation  │                                        │
│                   │   Agent     │                                        │
│                   │             │                                        │
│                   │ Quality     │                                        │
│                   │ Assessment  │                                        │
│                   │ Confidence  │                                        │
│                   │ Scoring     │                                        │
│                   └─────────────┘                                        │
│                           │                                               │
│                           ▼                                               │
│                   Confidence Report                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities Matrix

| Agent | Core Function | Input | Output | Enhancements |
|-------|---------------|-------|--------|--------------|
| **Orchestrator** | Workflow coordination + Batch management | PDF path(s) + config | Complete results + batch stats | Batch processing, Excel update logic, error isolation |
| **PDF Agent** | Text extraction + OCR fallback | PDF file | Raw text + tables + metadata | AWS Textract for scanned PDFs, automatic fallback |
| **LLM Agent** | Semantic processing + normalization | Raw text + tables | Raw JSON + SAP JSON | Unchanged (robust 3-phase processing) |
| **Validation Agent** | Quality assessment + confidence scoring | JSON data | Confidence score + report | Unchanged (comprehensive validation) |
| **Excel Agent** | File generation + intelligent updates | SAP JSON + paths | Excel file + operation details | Update existing files, backup creation, operation tracking |

---

## Component Details

### 1. Enhanced Orchestrator Agent

**Location**: `agents/orchestrator.py`

**Architecture Pattern**: Master Coordinator with Batch Processing

**Key Methods**:
```python
def execute(input_data) -> Dict:
    """Main entry point - routes to single or batch processing"""
    
def _execute_single(pdf_path, input_data) -> Dict:
    """Process single PDF through complete pipeline"""
    
def _execute_batch(input_data) -> Dict:
    """Process multiple PDFs with combined output"""
```

**Processing Flow**:
```
Input Analysis
    ↓
Route Decision (Single vs Batch)
    ↓
┌─────────────────┬─────────────────┐
│  Single Mode    │   Batch Mode    │
│                 │                 │
│ PDF → LLM →     │ For each PDF:   │
│ Validation →    │   PDF → LLM →   │
│ Excel           │   Validation    │
│                 │ Combine Results │
│                 │ Single Excel    │
└─────────────────┴─────────────────┘
    ↓
Enhanced Result with Operation Details
```

### 2. Enhanced PDF Agent

**Location**: `agents/pdf_agent.py`

**Architecture Pattern**: Primary-Fallback Processing

**Processing Decision Tree**:
```
PDF Input
    ↓
PDFPlumber Extraction
    ↓
Content Quality Check
    ├─ >100 chars ──→ Return PDFPlumber Results
    └─ <100 chars ──→ AWS Textract Fallback
                          ↓
                      OCR Processing
                          ↓
                      Structured Output
```

**Key Components**:
- **PDFPlumber Engine**: Fast text extraction for text-based PDFs
- **AWS Textract Engine**: OCR processing for scanned/image PDFs
- **Quality Detector**: Automatic method selection based on content
- **Output Normalizer**: Consistent format regardless of processing method

**Dependencies**:
```python
# Core PDF processing
pdfplumber>=0.10.3

# OCR fallback
boto3>=1.26.0          # AWS SDK
PyMuPDF>=1.23.0        # PDF to image conversion
Pillow>=9.5.0          # Image processing
```

### 3. LLM Agent (Unchanged - Robust Design)

**Location**: `agents/llm_agent.py`

**Architecture Pattern**: Three-Phase Processing Pipeline

**Phase Architecture**:
```
Phase 1: Invoice Detection
    ↓
Phase 2: Raw Data Extraction
    ↓
Phase 3: SAP Schema Normalization
```

**Technology Stack**:
- **Model**: Groq LLaMA 3.3 70B (`llama-3.3-70b-versatile`)
- **Response Format**: JSON mode
- **Temperature**: 0 (deterministic)

### 4. Validation Agent (Unchanged - Comprehensive)

**Location**: `agents/validation_agent.py`

**Architecture Pattern**: Multi-Layer Validation

**Validation Layers**:
1. **Required Field Validation**
2. **Data Type Validation**
3. **Business Rule Validation**
4. **Completeness Assessment**

### 5. Enhanced Excel Agent

**Location**: `agents/excel_agent.py`

**Architecture Pattern**: Intelligent File Management

**Operation Types**:
```
Input Analysis
    ↓
File Existence Check
    ├─ Exists + Same Path ──→ UPDATE (with backup)
    ├─ Exists + Diff Path ──→ CREATE_FROM_TEMPLATE
    └─ Not Exists ────────→ CREATE_NEW
```

**Backup Strategy**:
- **Automatic Creation**: Before any file updates
- **Naming Convention**: `{original}.backup_{YYYYMMDD_HHMMSS}.xlsx`
- **Safety Guarantee**: Zero data loss risk

---

## Data Flow Architecture

### Single PDF Processing Flow

```
PDF File (text-based or scanned)
    ↓
┌─────────────────────────────────────┐
│        Enhanced PDF Agent           │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ PDFPlumber  │  │ AWS Textract│   │
│  │ (Primary)   │  │ (Fallback)  │   │
│  └─────────────┘  └─────────────┘   │
└─────────────────┬───────────────────┘
                  ↓
Raw Text + Tables + Metadata + Processing Method
    ↓
┌─────────────────────────────────────┐
│           LLM Agent                 │
│  Phase 1: Detection                 │
│  Phase 2: Raw Extraction            │
│  Phase 3: SAP Normalization         │
└─────────────────┬───────────────────┘
                  ↓
Raw JSON + SAP JSON
    ├─ Saved: raw_invoice_TIMESTAMP.json
    └─ Saved: sap_invoice_TIMESTAMP.json
    ↓
┌─────────────────────────────────────┐
│        Validation Agent             │
│  • Required Fields Check            │
│  • Data Type Validation             │
│  • Business Rules                   │
│  • Confidence Scoring               │
└─────────────────┬───────────────────┘
                  ↓
Confidence Report
    └─ Saved: confidence_report_TIMESTAMP.json
    ↓
┌─────────────────────────────────────┐
│        Enhanced Excel Agent         │
│  • File Operation Decision          │
│  • Backup Creation (if updating)    │
│  • Row Generation & Append          │
│  • Operation Tracking               │
└─────────────────┬───────────────────┘
                  ↓
Excel File + Operation Details
    ├─ Updated: existing_file.xlsx
    ├─ Backup: existing_file.xlsx.backup_TIMESTAMP.xlsx
    └─ Stats: rows added, total rows, operation type
```

### Batch Processing Flow

```
Multiple PDF Files [PDF1, PDF2, ..., PDFn]
    ↓
┌─────────────────────────────────────┐
│     Enhanced Orchestrator           │
│     Batch Coordination              │
└─────────────────┬───────────────────┘
                  ↓
For Each PDF (Sequential Processing):
    ├─ Enhanced PDF Agent (with OCR fallback)
    ├─ LLM Agent (3-phase processing)
    ├─ Validation Agent
    └─ Collect Individual Results
    ↓
Result Aggregation:
    ├─ Combine all Raw JSONs
    ├─ Combine all SAP JSONs
    ├─ Aggregate Statistics
    └─ Track Per-File Status
    ↓
┌─────────────────────────────────────┐
│        Enhanced Excel Agent         │
│     Single Combined Update          │
└─────────────────┬───────────────────┘
                  ↓
Batch Output Files:
├─ batch_raw_invoices_TIMESTAMP.json
├─ batch_sap_invoices_TIMESTAMP.json
├─ batch_processing_report_TIMESTAMP.json
├─ updated_excel_file.xlsx
└─ backup_file.xlsx.backup_TIMESTAMP.xlsx (if updating)
```

---

## Processing Modes

### 1. Single PDF Mode

**Trigger**: `pdf_path` parameter provided
**Use Case**: Individual invoice processing
**Output**: 4 files (raw JSON, SAP JSON, confidence report, Excel)

### 2. Batch PDF Mode

**Trigger**: `pdf_paths` parameter with multiple files
**Use Case**: Bulk invoice processing
**Output**: 5-6 files (batch JSONs, batch report, confidence report, Excel, backup)

### 3. Excel Update Mode

**Trigger**: `base_excel_path` exists and equals `output_path`
**Use Case**: Continuous data accumulation
**Behavior**: Updates existing file with automatic backup

### 4. Excel Creation Mode

**Trigger**: `base_excel_path` doesn't exist or differs from `output_path`
**Use Case**: New file generation or template-based creation
**Behavior**: Creates new timestamped file

---

## Integration Points

### External Services

```
┌─────────────────────────────────────┐
│         Groq                        │
│  • LLaMA 3.3 70B Model              │
│  • JSON Response Format             │
│  • 3 API calls per PDF              │
│  • Deterministic Processing         │
└─────────────────────────────────────┘
                  ↑
                  │ HTTPS/REST API
                  ↓
┌─────────────────────────────────────┐
│      Invoice Processing System      │
└─────────────────────────────────────┘
                  ↑
                  │ AWS SDK
                  ↓
┌─────────────────────────────────────┐
│          AWS Textract               │
│  • Document Analysis                │
│  • Forms & Tables Detection         │
│  • OCR Processing                   │
│  • Per-page Processing              │
└─────────────────────────────────────┘
```

### File System Integration

```
Input Sources:
├─ Local PDF files
├─ Uploaded files (Streamlit)
└─ Batch file collections

Output Destinations:
├─ Local output directory
├─ Existing Excel files (updates)
├─ Backup directory (automatic)
└─ Temporary processing files
```

### Configuration Management

```
Environment Variables:
├─ GROQ_API_KEY
├─ GROQ_MODEL
├─ AWS_ACCESS_KEY_ID (optional)
├─ AWS_SECRET_ACCESS_KEY (optional)
└─ AWS_REGION (optional)

Configuration Files:
├─ config/sap_schema.py (SAP field definitions)
├─ .env (credentials)
└─ requirements.txt (dependencies)
```

---

## Error Handling Strategy

### Multi-Level Error Handling

```
┌─────────────────────────────────────┐
│           System Level              │
│  • Global exception handling        │
│  • Graceful degradation             │
│  • Status reporting                 │
└─────────────────┬───────────────────┘
                  ↓
┌─────────────────────────────────────┐
│         Orchestrator Level          │
│  • Pipeline error isolation         │
│  • Batch processing recovery        │
│  • Per-file error tracking          │
└─────────────────┬───────────────────┘
                  ↓
┌─────────────────────────────────────┐
│           Agent Level               │
│  • Individual agent error handling  │
│  • Fallback mechanisms              │
│  • Partial result preservation      │
└─────────────────────────────────────┘
```

### Error Recovery Mechanisms

1. **PDF Processing Errors**:
   - PDFPlumber fails → AWS Textract fallback
   - Textract fails → Graceful error with partial results

2. **Batch Processing Errors**:
   - Individual file failures don't stop batch
   - Per-file error isolation and reporting
   - Successful files still processed

3. **Excel Update Errors**:
   - File locked → Clear error message with retry suggestion
   - Backup creation fails → Warning but continue processing
   - Permission denied → Fallback to new file creation

---

## Extensibility Framework

### Adding New Processing Methods

```python
# Example: Adding new PDF processing method
class PDFAgent(BaseAgent):
    def execute(self, input_data):
        # Try primary method
        result = self._try_pdfplumber(input_data)
        if not self._is_sufficient(result):
            # Try fallback method
            result = self._try_textract(input_data)
            if not result:
                # Try new method
                result = self._try_new_method(input_data)
        return result
```

### Custom Agent Development

```python
from agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("CustomAgent")
    
    def execute(self, input_data):
        try:
            # Custom processing logic
            result = self._custom_processing(input_data)
            return {"status": "success", "data": result}
        except Exception as e:
            self.log_error(f"Custom processing failed: {e}")
            return {"status": "failed", "error": str(e)}
```

### Schema Extensions

```python
# config/sap_schema.py
SAP_COLUMNS = [
    # Existing columns...
    "CUSTOM_FIELD_1",
    "CUSTOM_FIELD_2",
    # New custom fields
]

DEFAULT_VALUES = {
    # Existing defaults...
    "CUSTOM_FIELD_1": "default_value",
    "CUSTOM_FIELD_2": "",
}
```

---

## Deployment Architecture

### Local Development

```
Development Environment:
├─ Python 3.8+ Runtime
├─ Local File System
├─ Environment Variables (.env)
├─ Streamlit Development Server
└─ Direct Agent Execution
```

### Production Deployment Options

#### Option 1: Single Server Deployment
```
Production Server:
├─ Python Application Server
├─ Streamlit Production Mode
├─ Local File Storage
├─ Environment Configuration
└─ Process Management (PM2/systemd)
```

#### Option 2: Containerized Deployment
```
Docker Container:
├─ Python Runtime Environment
├─ Application Code
├─ Dependencies (requirements.txt)
├─ Environment Variables
└─ Volume Mounts (file storage)
```

#### Option 3: Cloud Deployment
```
Cloud Platform (AWS/Azure/GCP):
├─ Container Service (ECS/ACI/Cloud Run)
├─ Object Storage (S3/Blob/Cloud Storage)
├─ Environment Management
├─ Auto-scaling Configuration
└─ Load Balancing (if needed)
```

### Scalability Considerations

```
Horizontal Scaling:
├─ Multiple Orchestrator Instances
├─ Queue-based Job Distribution
├─ Shared File Storage
└─ Load Balancer

Vertical Scaling:
├─ Increased CPU/Memory
├─ Batch Size Optimization
├─ Concurrent Processing
└─ Resource Monitoring
```

---

## Security Architecture

### Data Security

```
Security Layers:
├─ Environment Variable Protection
├─ API Key Management
├─ Local File System Permissions
├─ Temporary File Cleanup
└─ Backup File Protection
```

### Access Control

```
Access Management:
├─ File System Permissions
├─ Environment Variable Access
├─ API Endpoint Security
└─ User Interface Authentication (if deployed)
```

### Compliance Features

```
Compliance Support:
├─ Complete Audit Trail
├─ Processing History
├─ Backup Management
├─ Error Logging
└─ Data Retention Policies
```

---

This architecture document provides a comprehensive overview of the enhanced SAP Invoice Processing System, covering all aspects from high-level design to implementation details and deployment considerations.
