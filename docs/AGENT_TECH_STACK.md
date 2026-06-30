# Agent-Specific Tech Stack Breakdown

## 1. Base Agent (`agents/base_agent.py`)

### Core Technologies
- **Python Standard Library**
  - `abc` - Abstract Base Classes for agent interface
  - `logging` - Built-in logging framework
  - `typing` - Type hints and annotations

### Functionality
- **Abstract Base Class Pattern**: Defines common agent interface
- **Logging Framework**: Structured logging with agent identification
- **Type Safety**: Type hints for method signatures

### Dependencies
```python
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
```

---

## 2. PDF Agent (`agents/pdf_agent.py`)

### Primary Technologies
- **pdfplumber** - Fast text extraction from text-based PDFs
- **boto3** - AWS SDK for cloud services integration
- **PyMuPDF (fitz)** - PDF to image conversion for OCR
- **Pillow** - Image processing and manipulation

### Python Standard Library
- `json` - JSON data handling
- `os` - Operating system interface and environment variables
- `typing` - Type hints for method parameters
- `datetime` - Timestamp generation for processing metadata

### AWS Integration
- **botocore.exceptions** - AWS error handling
- **AWS Textract** - OCR service for scanned PDFs

### Processing Logic
- **Hybrid Processing**: PDFPlumber (primary) + Textract (fallback)
- **Quality Detection**: Automatic method selection based on content
- **Error Recovery**: Graceful fallback mechanisms

### Dependencies
```python
import pdfplumber
import boto3
import fitz  # PyMuPDF
import json
import os
from typing import Dict, Any, List
from datetime import datetime
from botocore.exceptions import ClientError
from .base_agent import BaseAgent
```

---

## 3. LLM Agent (`agents/llm_agent.py`)

### Primary Technologies
- **groq** - Groq client library
- **python-dotenv** - Environment variable management

### Python Standard Library
- `json` - JSON parsing and generation
- `os` - Environment variable access
- `datetime` - Timestamp generation
- `typing` - Type hints and annotations
- `re` - Regular expressions for text processing

### AI/ML Integration
- **Groq**
  - Model: `llama-3.3-70b-versatile`
  - Response Format: JSON mode
  - Temperature: 0 (deterministic)

### Processing Phases
1. **Invoice Detection**: Count invoices in PDF
2. **Raw Extraction**: Comprehensive data extraction
3. **SAP Normalization**: Schema alignment and business rules

### Advanced Features
- **Chunking Support**: Large document processing
- **Batch Processing**: Multiple invoice handling
- **Error Recovery**: Fallback mechanisms for API failures

### Dependencies
```python
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from groq import Groq
from dotenv import load_dotenv
from .base_agent import BaseAgent
from config.sap_schema import SAP_FIELD_DESCRIPTIONS, PDF_PRESENT_FIELDS, INFERRED_FIELDS
```

---

## 4. Validation Agent (`agents/validation_agent.py`)

### Primary Technologies
- **Python Built-in Type Checking**
  - `isinstance()` - Strict numeric type validation
  - `dict.get()` - Safe dictionary access

### Python Standard Library
- `typing` - Type hints for method signatures
- `re` - Regular expressions (via utils)

### Validation Mechanisms
- **Field Existence**: Dictionary key validation
- **Data Type Validation**: `isinstance(value, (int, float))`
- **Date Format Validation**: Custom regex and range checking
- **Business Rule Validation**: SAP-specific field requirements

### Validation Categories
- **Critical Issues**: Missing required fields, invalid data types
- **Warnings**: Missing optional fields, minor concerns
- **Confidence Scoring**: Quantitative quality assessment (0-100%)

### Dependencies
```python
from typing import Dict, Any, List
from .base_agent import BaseAgent
from config.sap_schema import SAP_COLUMNS, PDF_PRESENT_FIELDS, OPTIONAL_FIELDS
```

---

## 5. Excel Agent (`agents/excel_agent.py`)

### Primary Technologies
- **pandas** - Data manipulation and Excel operations
- **openpyxl** - Excel file reading, writing, and formatting

### Python Standard Library
- `os` - File system operations
- `datetime` - Timestamp generation for backups
- `typing` - Type hints and annotations

### Excel Operations
- **File Management**: Create, update, backup Excel files
- **Data Transformation**: JSON to Excel row conversion
- **Schema Mapping**: SAP field alignment
- **Backup System**: Automatic backup creation with timestamps

### Advanced Features
- **Operation Tracking**: Update vs. create detection
- **Backup Management**: Automatic backup before updates
- **Row Statistics**: Detailed operation reporting

### Dependencies
```python
import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any, List
from openpyxl import load_workbook
from .base_agent import BaseAgent
from config.sap_schema import SAP_COLUMNS, DEFAULT_VALUES
```

---

## 6. Orchestrator Agent (`agents/orchestrator.py`)

### Primary Technologies
- **Python Standard Library Only**
  - `json` - Data serialization and file operations
  - `os` - File system operations and directory management
  - `datetime` - Timestamp generation

### Orchestration Logic
- **Workflow Coordination**: Sequential agent execution
- **Batch Processing**: Multiple PDF handling
- **Error Isolation**: Per-file error handling
- **Result Aggregation**: Combined output generation

### Advanced Features
- **Single vs. Batch Mode**: Automatic processing mode detection
- **Excel Update Logic**: Intelligent file management
- **Comprehensive Reporting**: Detailed operation statistics

### Dependencies
```python
import json
import os
from datetime import datetime
from typing import Dict, Any
from .base_agent import BaseAgent
from .pdf_agent import PDFAgent
from .llm_agent import LLMAgent
from .excel_agent import ExcelAgent
from .validation_agent import ValidationAgent
```

---

## Utility Modules

### Date Utils (`utils/date_utils.py`)
- **datetime** - Date parsing and manipulation
- **typing** - Type hints for optional returns

### Validation Utils (`utils/validation_utils.py`)
- **re** - Regular expressions for pattern matching
- **typing** - Type hints for validation functions

---

## Configuration Module

### SAP Schema (`config/sap_schema.py`)
- **Pure Python Data Structures**
  - Lists for column definitions
  - Dictionaries for field descriptions and defaults
  - No external dependencies

---

## User Interface

### Streamlit App (`app.py`)
- **streamlit** - Web UI framework
- **pandas** - Data display and CSV generation
- **json** - JSON file handling
- **os** - File operations
- **time** - Execution time tracking
- **datetime** - Timestamp generation

---

## Agent Tech Stack Summary

| Agent | Primary Libraries | Python Std Lib | External Services | Key Features |
|-------|------------------|----------------|-------------------|--------------|
| **Base Agent** | None | `abc`, `logging`, `typing` | None | Abstract interface, logging |
| **PDF Agent** | `pdfplumber`, `boto3`, `PyMuPDF`, `Pillow` | `json`, `os`, `datetime`, `typing` | AWS Textract | Hybrid processing, OCR fallback |
| **LLM Agent** | `groq`, `python-dotenv` | `json`, `os`, `datetime`, `typing`, `re` | Groq | 3-phase processing, chunking |
| **Validation Agent** | None | `typing` | None | Type checking, confidence scoring |
| **Excel Agent** | `pandas`, `openpyxl` | `os`, `datetime`, `typing` | None | File management, backups |
| **Orchestrator** | None | `json`, `os`, `datetime`, `typing` | None | Workflow coordination, batch processing |

## Technology Distribution

### External Libraries (10 total)
- **PDF Processing**: `pdfplumber`, `boto3`, `PyMuPDF`, `Pillow` (4)
- **AI/ML**: `groq` (1)
- **Data Processing**: `pandas`, `openpyxl` (2)
- **Configuration**: `python-dotenv`, `pydantic` (2)
- **UI**: `streamlit` (1)

### Python Standard Library (Most Used)
- **json** - Used by 4 agents (PDF, LLM, Orchestrator, App)
- **os** - Used by 4 agents (PDF, LLM, Excel, Orchestrator)
- **datetime** - Used by 4 agents (PDF, LLM, Excel, Orchestrator)
- **typing** - Used by all 6 agents (universal type hints)

### External Services
- **Groq** - Used by LLM Agent only
- **AWS Textract** - Used by PDF Agent only (optional fallback)

## Agent Independence & Modularity

### Self-Contained Agents
- **Validation Agent**: No external dependencies (pure Python)
- **Orchestrator Agent**: No external dependencies (coordination only)

### Service-Dependent Agents
- **PDF Agent**: Requires AWS credentials for OCR fallback
- **LLM Agent**: Requires Groq API key (critical dependency)

### Data Processing Agents
- **Excel Agent**: Requires pandas/openpyxl for file operations
- **Base Agent**: Provides common logging infrastructure

This agent-specific breakdown shows how the system maintains modularity while leveraging specialized technologies for each processing stage.