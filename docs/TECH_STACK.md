# SAP Invoice Processing System - Complete Tech Stack

## Core Runtime Environment

### Programming Language
- **Python 3.8+** (Required minimum version)
  - Object-oriented programming with inheritance
  - Type hints and annotations (`typing` module)
  - Abstract base classes (`abc` module)
  - Exception handling and logging

## Python Dependencies & Libraries

### Core Framework & UI
```
streamlit                    # Web UI framework for the main application interface
```

### PDF Processing & OCR
```
pdfplumber                   # Primary PDF text extraction library
boto3                        # AWS SDK for Textract OCR fallback
PyMuPDF (fitz)              # PDF to image conversion for OCR processing
Pillow                       # Image processing and manipulation
botocore                     # AWS core library (dependency of boto3)
```

### AI & Machine Learning
```
groq                         # Groq client library
```

### Data Processing & Excel
```
pandas                       # Data manipulation and analysis
openpyxl                     # Excel file reading/writing and formatting
```

### Configuration & Utilities
```
python-dotenv                # Environment variable management
pydantic                     # Data validation and settings management
```

### Built-in Python Libraries
```
json                         # JSON parsing and generation
os                           # Operating system interface
sys                          # System-specific parameters and functions
datetime                     # Date and time handling
time                         # Time-related functions
typing                       # Type hints and annotations
abc                          # Abstract base classes
logging                      # Logging framework
re                           # Regular expressions
```

## External Services & APIs

### AI/ML Services
- **Groq**
  - Model: `llama-3.3-70b-versatile`
  - Response Format: JSON mode
  - Temperature: 0 (deterministic processing)
  - Usage: 3 API calls per PDF (detection, extraction, normalization)

### Cloud Services (Optional)
- **AWS Textract**
  - Document analysis and OCR
  - Forms and tables detection
  - Fallback for scanned PDFs
  - Per-page processing capability

## Development & Runtime Environment

### System Requirements
- **Operating System**: Windows (cmd shell), Linux, macOS
- **Python Version**: 3.8 or higher
- **CPU**: 2+ cores recommended (4+ for batch processing)
- **RAM**: 4GB minimum, 8GB recommended (12GB for large batches)
- **Storage**: 1GB for system, additional for outputs and backups
- **Network**: Internet connection for Groq API and AWS Textract

### Environment Configuration
```bash
# Groq Configuration (Required)
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile

# AWS Configuration (Optional - for OCR fallback)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

## Architecture Components

### Multi-Agent System
- **Base Agent Pattern**: Abstract base class with logging
- **Orchestrator Pattern**: Master coordinator for workflow management
- **Pipeline Architecture**: Sequential agent execution with error handling

### Data Processing Pipeline
```
PDF Input → PDF Agent → LLM Agent → Validation Agent → Excel Agent → Output
```

### File System Integration
- **Input Sources**: Local PDF files, uploaded files (Streamlit)
- **Output Destinations**: Local output directory, existing Excel files
- **Backup System**: Automatic backup creation with timestamps
- **Temporary Processing**: Automatic cleanup of uploaded files

## Data Formats & Standards

### Input Formats
- **PDF Files**: Text-based and scanned/image PDFs
- **Configuration**: Environment variables (.env files)
- **Schema**: Python dictionaries and JSON objects

### Output Formats
- **Excel Files**: .xlsx format with 35 SAP columns
- **JSON Files**: Raw extraction and SAP-normalized data
- **Reports**: Confidence reports and batch processing reports

### Data Standards
- **Dates**: ISO format (YYYY-MM-DD)
- **Currency**: 3-letter codes (USD, EUR, AED)
- **Amounts**: Numeric values (int/float)
- **Text Encoding**: UTF-8

## Security & Configuration

### Credential Management
- **Environment Variables**: API keys and secrets stored in .env files
- **No Hardcoded Credentials**: All sensitive data externalized
- **File System Permissions**: Proper access control for files and directories

### Data Security
- **Local Processing**: Most processing done locally
- **External API Calls**: Only to Groq and AWS Textract
- **Temporary File Cleanup**: Automatic removal of uploaded files
- **Backup Protection**: Automatic backup creation before file updates

## Development Tools & Utilities

### Validation & Testing
- **Type Checking**: Python's `isinstance()` for data type validation
- **Date Validation**: Custom regex and range validation
- **Currency Validation**: Regex pattern matching
- **Amount Validation**: Try-catch with float conversion

### Logging & Monitoring
- **Python Logging**: Built-in logging framework
- **Agent-Level Logging**: Individual agent identification
- **Structured Logging**: INFO, WARNING, ERROR levels
- **Timestamp Tracking**: All operations timestamped

### Error Handling
- **Multi-Level**: System, orchestrator, and agent-level error handling
- **Graceful Degradation**: Partial results when possible
- **Fallback Mechanisms**: OCR fallback, retry logic
- **Status Reporting**: Clear success/failure indicators

## Deployment Options

### Local Development
```
Python 3.8+ Runtime
Local File System
Environment Variables (.env)
Streamlit Development Server
Direct Agent Execution
```

### Production Deployment
```
# Option 1: Single Server
Python Application Server
Streamlit Production Mode
Local File Storage
Environment Configuration
Process Management (PM2/systemd)

# Option 2: Containerized
Docker Container
Python Runtime Environment
Application Code
Dependencies (requirements.txt)
Environment Variables
Volume Mounts (file storage)

# Option 3: Cloud Platform
Container Service (ECS/ACI/Cloud Run)
Object Storage (S3/Blob/Cloud Storage)
Environment Management
Auto-scaling Configuration
Load Balancing (if needed)
```

## Performance & Scalability

### Processing Performance
- **PDF Extraction**: <1 second (PDFPlumber), 3-8 seconds/page (Textract)
- **LLM Processing**: 5-15 seconds (3 Groq API calls)
- **Validation**: <1 second (local processing)
- **Excel Generation**: <1 second (single), 2-5 seconds (batch)

### Scalability Features
- **Batch Processing**: Multiple PDFs processed sequentially
- **Memory Optimization**: Individual PDF processing with result aggregation
- **Error Isolation**: Per-file error handling prevents batch failures
- **Intelligent Fallback**: Automatic OCR when needed

## Integration Capabilities

### File System Integration
- **Multiple Upload Modes**: Single PDF and batch processing
- **File Management**: Update existing files vs. create new files
- **Backup System**: Automatic backup creation with timestamps
- **Output Organization**: Structured output directory with multiple file types

### API Integration
- **RESTful APIs**: Groq REST API
- **AWS SDK**: Boto3 for Textract integration
- **JSON Communication**: Structured data exchange
- **Error Recovery**: Automatic retry and fallback mechanisms

## Quality Assurance

### Data Validation
- **Multi-Layer Validation**: Field existence, data types, business rules
- **Confidence Scoring**: Quantitative quality metrics (0-100%)
- **Issue Classification**: Critical issues vs. warnings
- **Detailed Reporting**: Specific error messages with location info

### Testing Framework
- **Unit Testing**: Individual agent functionality
- **Integration Testing**: End-to-end pipeline testing
- **Validation Testing**: Data type and format validation
- **Error Scenario Testing**: Failure handling and recovery

## Summary

The SAP Invoice Processing System uses a modern, robust tech stack built on:

- **Python 3.8+** as the core runtime
- **10 external libraries** for specialized functionality
- **2 cloud AI services** (Groq + AWS Textract)
- **Multi-agent architecture** for modularity and maintainability
- **Comprehensive validation** and error handling
- **Flexible deployment options** from local to cloud
- **Enterprise-grade features** including backups, logging, and audit trails

This tech stack provides a solid foundation for processing diverse PDF types, handling batch operations, and maintaining high data quality while being extensible for future enhancements.