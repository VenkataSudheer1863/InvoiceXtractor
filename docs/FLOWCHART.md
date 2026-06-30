# SAP Invoice Processing System - Complete Flowcharts

This document contains comprehensive flowcharts for the SAP Invoice Processing System, showing the complete data flow, process flow, and component interactions including all recent enhancements.

---

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph UI ["User Interfaces"]
        UI1[Streamlit Web UI<br/>Single & Multiple PDFs]
        UI2[Command Line Interface<br/>Batch Processing]
        UI3[Python API<br/>Programmatic Access]
    end
    
    subgraph CORE ["Core Multi-Agent System"]
        ORCH[Orchestrator Agent<br/>Workflow Coordinator<br/>Batch Processing]
        
        subgraph AGENTS ["Processing Agents"]
            PDF[PDF Agent<br/>pdfplumber + Textract Fallback]
            LLM[LLM Agent<br/>3-Phase AI Processing]
            VAL[Validation Agent<br/>Quality Assessment]
            XLS[Excel Agent<br/>File Generation & Updates]
        end
    end
    
    subgraph EXT ["External Services"]
        GROQ[Groq<br/>LLaMA 3.3 70B]
        AWS[AWS Textract<br/>OCR Fallback]
    end
    
    subgraph DATA ["Data Storage"]
        INPUT[Input PDFs<br/>Single or Multiple]
        OUTPUT[Output Files<br/>JSON + Excel + Reports]
        BACKUP[Automatic Backups<br/>Excel Updates]
    end
    
    UI1 --> ORCH
    UI2 --> ORCH
    UI3 --> ORCH
    
    ORCH --> PDF
    ORCH --> LLM
    ORCH --> VAL
    ORCH --> XLS
    
    LLM <--> GROQ
    PDF <--> AWS
    
    PDF --> INPUT
    XLS --> OUTPUT
    XLS --> BACKUP
    
    style ORCH fill:#e1f5fe
    style LLM fill:#f3e5f5
    style GROQ fill:#fff3e0
    style AWS fill:#e8f5e8
    style OUTPUT fill:#e8f5e8
```

---

## 2. Complete Data Flow Pipeline (Enhanced)

```mermaid
flowchart TD
    START([PDF Input<br/>Single or Multiple]) --> BATCH_CHECK{Multiple PDFs?}
    
    BATCH_CHECK -->|No| SINGLE_FLOW[Single PDF Processing]
    BATCH_CHECK -->|Yes| BATCH_FLOW[Batch PDF Processing]
    
    SINGLE_FLOW --> PDF_AGENT[PDF Agent<br/>pdfplumber extraction]
    BATCH_FLOW --> BATCH_PDF[Process Each PDF<br/>in Sequence]
    
    PDF_AGENT --> QUALITY_CHECK{Text Quality<br/>> 100 chars?}
    QUALITY_CHECK -->|No| TEXTRACT[AWS Textract Fallback<br/>OCR + Forms + Tables]
    QUALITY_CHECK -->|Yes| RAW_DATA[Raw Text + Tables + Metadata]
    TEXTRACT --> RAW_DATA
    
    BATCH_PDF --> BATCH_RAW[Collect All Raw Data]
    BATCH_RAW --> RAW_DATA
    
    RAW_DATA --> SIZE_CHECK{Document Size<br/>> 50KB or > 10 invoices?}
    SIZE_CHECK -->|Yes| CHUNKING[Intelligent Chunking<br/>Invoice Boundaries]
    SIZE_CHECK -->|No| LLM_DETECT[LLM Agent - Phase 1<br/>Invoice Detection]
    CHUNKING --> LLM_DETECT
    
    LLM_DETECT --> DETECT_OUTPUT[Number of Invoices Detected]
    DETECT_OUTPUT --> LLM_EXTRACT[LLM Agent - Phase 2<br/>Raw Data Extraction]
    
    LLM_EXTRACT --> EXTRACT_CHECK{> 10 invoices?}
    EXTRACT_CHECK -->|Yes| BATCH_EXTRACT[Batch Extraction<br/>Process in Chunks]
    EXTRACT_CHECK -->|No| RAW_JSON[Raw JSON<br/>Lossless Format]
    BATCH_EXTRACT --> RAW_JSON
    
    RAW_JSON --> SAVE_RAW[Save: raw_invoice_TIMESTAMP.json]
    RAW_JSON --> LLM_NORMALIZE[LLM Agent - Phase 3<br/>SAP Normalization]
    
    LLM_NORMALIZE --> NORM_CHECK{> 10 invoices?}
    NORM_CHECK -->|Yes| BATCH_NORM[Batch Normalization<br/>15 invoices per batch]
    NORM_CHECK -->|No| SAP_JSON[SAP JSON<br/>Schema-Aligned Format]
    BATCH_NORM --> SAP_JSON
    
    SAP_JSON --> SAVE_SAP[Save: sap_invoice_TIMESTAMP.json]
    SAP_JSON --> VALIDATION[Validation Agent<br/>Quality Assessment]
    RAW_JSON --> VALIDATION
    
    VALIDATION --> CONF_SCORE[Confidence Score<br/>0.0 - 1.0]
    VALIDATION --> VAL_REPORT[Validation Report<br/>Issues + Warnings]
    
    CONF_SCORE --> SAVE_CONF[Save: confidence_report_TIMESTAMP.json]
    VAL_REPORT --> SAVE_CONF
    
    SAP_JSON --> EXCEL_AGENT[Excel Agent<br/>File Generation/Update]
    EXCEL_AGENT --> EXCEL_CHECK{Base Excel Exists?}
    EXCEL_CHECK -->|Yes| UPDATE_EXCEL[Update Existing Excel<br/>Create Backup First]
    EXCEL_CHECK -->|No| CREATE_EXCEL[Create New Excel File]
    
    UPDATE_EXCEL --> EXCEL_OUTPUT[Excel File<br/>35 SAP Columns]
    CREATE_EXCEL --> EXCEL_OUTPUT
    
    EXCEL_OUTPUT --> SAVE_EXCEL[Save: Updated or New Excel]
    
    SAVE_RAW --> COMPLETE[Processing Complete<br/>4+ Output Files]
    SAVE_SAP --> COMPLETE
    SAVE_CONF --> COMPLETE
    SAVE_EXCEL --> COMPLETE
    
    COMPLETE --> END([Results Available<br/>Download & Audit Trail])
    
    style START fill:#e8f5e8
    style END fill:#e8f5e8
    style TEXTRACT fill:#fff3e0
    style RAW_JSON fill:#fff3e0
    style SAP_JSON fill:#e3f2fd
    style CONF_SCORE fill:#f1f8e9
    style EXCEL_OUTPUT fill:#fce4ec
    style UPDATE_EXCEL fill:#e8f5e8
```

---

## 3. PDF Agent with Textract Fallback

```mermaid
flowchart TD
    PDF_INPUT[PDF File Input] --> PDFPLUMBER[PDFPlumber Extraction<br/>Fast Text-Based Processing]
    
    PDFPLUMBER --> QUALITY_CHECK{Text Quality Check<br/>Length > 100 chars?}
    QUALITY_CHECK -->|Yes| SUCCESS_OUTPUT[Successful Extraction<br/>Text + Tables + Metadata]
    QUALITY_CHECK -->|No| TEXTRACT_INIT{AWS Textract<br/>Available?}
    
    TEXTRACT_INIT -->|No| MINIMAL_OUTPUT[Return Minimal Text<br/>Log Warning]
    TEXTRACT_INIT -->|Yes| CONVERT_IMAGES[Convert PDF to Images<br/>PyMuPDF 2x Resolution]
    
    CONVERT_IMAGES --> PROCESS_PAGES[Process Each Page<br/>with Textract]
    
    PROCESS_PAGES --> TEXTRACT_FORMS[Analyze Document<br/>Forms + Tables Mode]
    TEXTRACT_FORMS --> FORMS_SUCCESS{Forms Analysis<br/>Successful?}
    
    FORMS_SUCCESS -->|Yes| EXTRACT_STRUCTURED[Extract Structured Data<br/>Key-Value Pairs + Tables]
    FORMS_SUCCESS -->|No| TEXTRACT_TEXT[Fallback to Text Detection<br/>Basic OCR Mode]
    
    TEXTRACT_TEXT --> EXTRACT_TEXT[Extract Text Lines<br/>OCR Results]
    
    EXTRACT_STRUCTURED --> COMBINE_DATA[Combine All Data<br/>Text + Forms + Tables]
    EXTRACT_TEXT --> COMBINE_DATA
    
    COMBINE_DATA --> TEXTRACT_OUTPUT[Textract Output<br/>Structured JSON Format]
    
    SUCCESS_OUTPUT --> FINAL_OUTPUT[Final PDF Agent Output<br/>Consistent Format]
    TEXTRACT_OUTPUT --> FINAL_OUTPUT
    MINIMAL_OUTPUT --> FINAL_OUTPUT
    
    FINAL_OUTPUT --> METADATA[Add Processing Metadata<br/>Method Used + Statistics]
    
    style PDF_INPUT fill:#e3f2fd
    style PDFPLUMBER fill:#e8f5e8
    style TEXTRACT_FORMS fill:#fff3e0
    style FINAL_OUTPUT fill:#e8f5e8
    style METADATA fill:#f1f8e9
```

---

## 4. LLM Agent Three-Phase Processing (Enhanced)

```mermaid
flowchart TD
    INPUT_TEXT[Raw Text + Tables] --> DOC_SIZE{Document Size<br/>> 50KB or > 10 invoices?}
    
    DOC_SIZE -->|Yes| CHUNKING[Intelligent Chunking<br/>Invoice Boundary Detection]
    DOC_SIZE -->|No| PHASE1[Phase 1: Detection]
    CHUNKING --> PHASE1
    
    subgraph P1 ["Phase 1: Invoice Detection"]
        PHASE1 --> DETECT_PROMPT[Detection Prompt<br/>Count invoices in document]
        DETECT_PROMPT --> GROQ1[Groq API Call 1<br/>Temperature: 0]
        GROQ1 --> DETECT_RESULT[Number of Invoices: N]
    end
    
    DETECT_RESULT --> PHASE2[Phase 2: Raw Extraction]
    
    subgraph P2 ["Phase 2: Lossless Extraction"]
        PHASE2 --> EXTRACT_PROMPT[Extraction Prompt<br/>Extract ALL invoice data]
        EXTRACT_PROMPT --> CHUNK_PROCESS{Chunked Processing?}
        CHUNK_PROCESS -->|Yes| GROQ2_BATCH[Multiple API Calls<br/>Process Each Chunk]
        CHUNK_PROCESS -->|No| GROQ2[Single API Call<br/>Full Document]
        GROQ2 --> RAW_JSON_OUT[Raw JSON Output<br/>Lossless, Unstructured]
        GROQ2_BATCH --> MERGE_CHUNKS[Merge Chunk Results]
        MERGE_CHUNKS --> RAW_JSON_OUT
    end
    
    RAW_JSON_OUT --> PHASE3[Phase 3: SAP Normalization]
    
    subgraph P3 ["Phase 3: Schema Normalization"]
        PHASE3 --> NORM_PROMPT[Normalization Prompt<br/>Apply SAP Business Rules]
        NORM_PROMPT --> BATCH_NORM_CHECK{> 10 invoices?}
        BATCH_NORM_CHECK -->|Yes| BATCH_NORM[Batch Normalization<br/>15 invoices per batch]
        BATCH_NORM_CHECK -->|No| GROQ3[Single API Call<br/>Full Normalization]
        BATCH_NORM --> GROQ3_BATCH[Multiple API Calls<br/>Normalize Batches]
        GROQ3 --> SAP_JSON_OUT[SAP JSON Output<br/>Schema-Aligned]
        GROQ3_BATCH --> MERGE_NORM[Merge Normalized Results]
        MERGE_NORM --> SAP_JSON_OUT
    end
    
    SAP_JSON_OUT --> GRANULAR_CHECK[Granularity Validation<br/>Each charge separate line item]
    GRANULAR_CHECK --> FINAL_OUTPUT[Final LLM Output<br/>Raw JSON + SAP JSON]
    
    style P1 fill:#e3f2fd
    style P2 fill:#fff3e0
    style P3 fill:#e8f5e8
    style RAW_JSON_OUT fill:#fff3e0
    style SAP_JSON_OUT fill:#e3f2fd
    style GRANULAR_CHECK fill:#f1f8e9
```

---

## 5. Orchestrator Agent Workflow (Enhanced)

```mermaid
flowchart TD
    START([Orchestrator Execute]) --> INPUT_CHECK{Input Type Check}
    
    INPUT_CHECK -->|pdf_path| SINGLE_MODE[Single PDF Mode]
    INPUT_CHECK -->|pdf_paths list| BATCH_CHECK{List Length > 1?}
    INPUT_CHECK -->|No input| ERROR_INPUT[Return Error:<br/>No PDF input provided]
    
    BATCH_CHECK -->|Yes| BATCH_MODE[Batch PDF Mode]
    BATCH_CHECK -->|No| SINGLE_MODE
    
    SINGLE_MODE --> INIT_SINGLE[Initialize Single Processing<br/>PDF, LLM, Validation, Excel Agents]
    BATCH_MODE --> INIT_BATCH[Initialize Batch Processing<br/>Multiple PDF Handling]
    
    INIT_SINGLE --> STEP1[Step 1: PDF Agent]
    INIT_BATCH --> BATCH_LOOP[For Each PDF File...]
    
    BATCH_LOOP --> STEP1
    STEP1 --> PDF_EXEC[pdf_agent execute]
    PDF_EXEC --> PDF_CHECK{PDF Success?}
    PDF_CHECK -->|No| ERROR_PDF[Log PDF Error<br/>Continue or Fail]
    PDF_CHECK -->|Yes| STEP2[Step 2: LLM Agent]
    
    STEP2 --> LLM_EXEC[llm_agent execute]
    LLM_EXEC --> LLM_CHECK{LLM Success?}
    LLM_CHECK -->|No| ERROR_LLM[Log LLM Error<br/>Continue or Fail]
    LLM_CHECK -->|Yes| SAVE_INTERMEDIATE[Save Intermediate Files<br/>raw_invoice_*.json<br/>sap_invoice_*.json]
    
    SAVE_INTERMEDIATE --> STEP3[Step 3: Validation Agent]
    STEP3 --> VAL_EXEC[validation_agent execute]
    VAL_EXEC --> VAL_CHECK{Validation Success?}
    VAL_CHECK -->|No| ERROR_VAL[Log Validation Warning<br/>Continue with Low Score]
    VAL_CHECK -->|Yes| SAVE_CONFIDENCE[Save Confidence Report<br/>confidence_report_*.json]
    
    SAVE_CONFIDENCE --> BATCH_CONTINUE{More PDFs in Batch?}
    BATCH_CONTINUE -->|Yes| BATCH_LOOP
    BATCH_CONTINUE -->|No| STEP4[Step 4: Excel Agent]
    
    STEP4 --> EXCEL_MODE{Excel Operation Mode}
    EXCEL_MODE -->|Update Existing| UPDATE_EXCEL[Update Base Excel File<br/>Create Backup First]
    EXCEL_MODE -->|Create New| CREATE_EXCEL[Create New Excel File<br/>With Timestamp]
    
    UPDATE_EXCEL --> EXCEL_EXEC[excel_agent execute]
    CREATE_EXCEL --> EXCEL_EXEC
    EXCEL_EXEC --> EXCEL_CHECK{Excel Success?}
    EXCEL_CHECK -->|No| ERROR_EXCEL[Return Error:<br/>Excel generation failed]
    EXCEL_CHECK -->|Yes| SAVE_EXCEL[Save Excel File<br/>Track Operation Type]
    
    SAVE_EXCEL --> AGGREGATE[Aggregate Results<br/>Combine All Outputs + Statistics]
    AGGREGATE --> SUCCESS[Return Success Result<br/>All Paths + Metadata + Counts]
    
    ERROR_INPUT --> END([End])
    ERROR_PDF --> END
    ERROR_LLM --> END
    ERROR_EXCEL --> END
    SUCCESS --> END
    
    style START fill:#e8f5e8
    style END fill:#e8f5e8
    style SUCCESS fill:#e8f5e8
    style BATCH_MODE fill:#e3f2fd
    style UPDATE_EXCEL fill:#fff3e0
    style ERROR_INPUT fill:#ffebee
    style ERROR_PDF fill:#ffebee
    style ERROR_LLM fill:#ffebee
    style ERROR_EXCEL fill:#ffebee
```

---

## 6. Excel Agent Enhanced Processing

```mermaid
flowchart TD
    SAP_JSON[SAP JSON Input] --> INIT_ROWS[Initialize Empty Rows List]
    
    INIT_ROWS --> LOOP_INVOICES[For Each Invoice in SAP JSON...]
    LOOP_INVOICES --> GET_HEADER[Extract Header Fields<br/>BELNR, BLDAT, WAERS, etc.]
    
    GET_HEADER --> LOOP_ITEMS[For Each Line Item...]
    LOOP_ITEMS --> GRANULAR_CHECK[Granularity Check<br/>Each charge separate?]
    GRANULAR_CHECK --> MERGE_FIELDS[Merge Header + Line Item<br/>Create Complete Row]
    
    MERGE_FIELDS --> APPLY_DEFAULTS[Apply Default Values<br/>BLART=KR, BUKRS=013, etc.]
    APPLY_DEFAULTS --> BSCHL_LOGIC[Apply BSCHL Logic<br/>40 for items, 31 for total]
    BSCHL_LOGIC --> ADD_ROW[Add Row to Rows List]
    
    ADD_ROW --> MORE_ITEMS{More Line Items?}
    MORE_ITEMS -->|Yes| LOOP_ITEMS
    MORE_ITEMS -->|No| MORE_INVOICES{More Invoices?}
    
    MORE_INVOICES -->|Yes| LOOP_INVOICES
    MORE_INVOICES -->|No| EXCEL_MODE{Excel Operation Mode}
    
    EXCEL_MODE -->|Update Existing| LOAD_EXISTING[Load Existing Excel<br/>Check if Same Path]
    EXCEL_MODE -->|Create New| CREATE_NEW[Create New DataFrame<br/>With SAP Columns]
    
    LOAD_EXISTING --> BACKUP_CHECK{Same Path as Output?}
    BACKUP_CHECK -->|Yes| CREATE_BACKUP[Create Automatic Backup<br/>filename.backup_timestamp.xlsx]
    BACKUP_CHECK -->|No| APPEND_ROWS[Append New Rows<br/>to Existing Data]
    CREATE_BACKUP --> APPEND_ROWS
    
    CREATE_NEW --> APPEND_ROWS
    APPEND_ROWS --> SAVE_EXCEL[Save Excel File<br/>with openpyxl Engine]
    
    SAVE_EXCEL --> TRACK_OPERATION[Track Operation Details<br/>Updated/Created/From Template]
    TRACK_OPERATION --> RETURN_RESULT[Return Result<br/>Path + Counts + Operation Type]
    
    style SAP_JSON fill:#e3f2fd
    style RETURN_RESULT fill:#e8f5e8
    style GRANULAR_CHECK fill:#f1f8e9
    style CREATE_BACKUP fill:#fff3e0
    style TRACK_OPERATION fill:#e8f5e8
```

---

## 7. Batch Processing Flow

```mermaid
flowchart TD
    BATCH_INPUT[Multiple PDF Paths] --> INIT_BATCH[Initialize Batch Processing<br/>Empty Results Structure]
    
    INIT_BATCH --> EXCEL_DECISION[Determine Excel Output Path<br/>Update Existing or Create New]
    EXCEL_DECISION --> PROCESS_LOOP[For Each PDF File...]
    
    PROCESS_LOOP --> FILE_PROCESS[Process Single PDF<br/>PDF → LLM → Validation]
    FILE_PROCESS --> FILE_SUCCESS{Processing<br/>Successful?}
    
    FILE_SUCCESS -->|Yes| COLLECT_SUCCESS[Add to Successful Files<br/>Store SAP JSON + Stats]
    FILE_SUCCESS -->|No| COLLECT_FAILED[Add to Failed Files<br/>Store Error Details]
    
    COLLECT_SUCCESS --> MORE_FILES{More Files<br/>to Process?}
    COLLECT_FAILED --> MORE_FILES
    
    MORE_FILES -->|Yes| PROCESS_LOOP
    MORE_FILES -->|No| COMBINE_DATA[Combine All SAP JSONs<br/>Single Merged Structure]
    
    COMBINE_DATA --> BATCH_EXCEL[Generate Combined Excel<br/>All Invoices in One File]
    BATCH_EXCEL --> SAVE_BATCH_FILES[Save Batch Output Files<br/>Combined JSONs + Reports]
    
    SAVE_BATCH_FILES --> BATCH_STATS[Calculate Batch Statistics<br/>Files, Invoices, Line Items, Rows]
    BATCH_STATS --> BATCH_REPORT[Generate Batch Report<br/>Success/Failure Details]
    
    BATCH_REPORT --> RETURN_BATCH[Return Batch Results<br/>Combined Outputs + Statistics]
    
    style BATCH_INPUT fill:#e3f2fd
    style RETURN_BATCH fill:#e8f5e8
    style COLLECT_SUCCESS fill:#e8f5e8
    style COLLECT_FAILED fill:#ffebee
    style COMBINE_DATA fill:#fff3e0
    style BATCH_STATS fill:#f1f8e9
```

---

## 8. User Interface Flow (Enhanced Streamlit)

```mermaid
flowchart TD
    START([User Opens Streamlit App]) --> LOAD_UI[Load Web Interface<br/>Enhanced with Batch Support]
    
    LOAD_UI --> DISPLAY_FORM[Display Upload Form<br/>Single or Multiple PDF Mode]
    DISPLAY_FORM --> MODE_SELECT[User Selects Upload Mode<br/>Single PDF or Multiple PDFs]
    
    MODE_SELECT --> UPLOAD_MODE{Upload Mode<br/>Selected}
    UPLOAD_MODE -->|Single| SINGLE_UPLOAD[Single PDF File Uploader]
    UPLOAD_MODE -->|Multiple| MULTI_UPLOAD[Multiple PDF Files Uploader<br/>accept_multiple_files=True]
    
    SINGLE_UPLOAD --> FILES_UPLOADED{Files Uploaded?}
    MULTI_UPLOAD --> FILES_UPLOADED
    
    FILES_UPLOADED -->|No| MODE_SELECT
    FILES_UPLOADED -->|Yes| SHOW_CONFIG[Show Configuration<br/>Base Excel Path, Output Directory]
    
    SHOW_CONFIG --> PROCESS_BUTTON[Show Process Button<br/>Dynamic Label Based on File Count]
    PROCESS_BUTTON --> BUTTON_CLICKED{Button Clicked?}
    
    BUTTON_CLICKED -->|No| PROCESS_BUTTON
    BUTTON_CLICKED -->|Yes| SAVE_TEMP[Save Uploaded Files<br/>to Temp Directory]
    
    SAVE_TEMP --> SHOW_PROGRESS[Show Progress Spinner<br/>Processing invoice(s)...]
    SHOW_PROGRESS --> CALL_ORCHESTRATOR[Call Orchestrator<br/>Single or Batch Mode]
    
    CALL_ORCHESTRATOR --> PROCESSING{Processing<br/>Successful?}
    PROCESSING -->|No| SHOW_ERROR[Display Error Message<br/>with Detailed Information]
    PROCESSING -->|Yes| SHOW_SUCCESS[Display Success Message<br/>with Statistics]
    
    SHOW_SUCCESS --> BATCH_CHECK{Batch Processing<br/>Results?}
    BATCH_CHECK -->|Yes| DISPLAY_BATCH_TABS[Display Batch Result Tabs<br/>Rows, JSONs, Batch Report, Downloads]
    BATCH_CHECK -->|No| DISPLAY_SINGLE_TABS[Display Single Result Tabs<br/>Rows, Raw JSON, SAP JSON, Downloads]
    
    DISPLAY_BATCH_TABS --> SHOW_DOWNLOADS[Show Download Buttons<br/>All Output Files + Batch Report]
    DISPLAY_SINGLE_TABS --> SHOW_DOWNLOADS
    
    SHOW_DOWNLOADS --> WAIT_ACTION[Wait for User Action...]
    WAIT_ACTION --> DOWNLOAD_CLICKED{Download Button<br/>Clicked?}
    
    DOWNLOAD_CLICKED -->|Yes| SERVE_FILE[Serve File Download<br/>Excel, JSON, or Report]
    DOWNLOAD_CLICKED -->|No| NEW_UPLOAD{New Files<br/>Uploaded?}
    
    SERVE_FILE --> WAIT_ACTION
    NEW_UPLOAD -->|Yes| SAVE_TEMP
    NEW_UPLOAD -->|No| WAIT_ACTION
    
    SHOW_ERROR --> WAIT_ACTION
    
    style START fill:#e8f5e8
    style SHOW_SUCCESS fill:#e8f5e8
    style SHOW_ERROR fill:#ffebee
    style DISPLAY_BATCH_TABS fill:#e3f2fd
    style MULTI_UPLOAD fill:#fff3e0
    style SERVE_FILE fill:#e8f5e8
```

---

## 9. Complete System Integration Flow (Current State)

```mermaid
graph TB
    subgraph IL ["Input Layer"]
        PDF_SINGLE[Single PDF Files<br/>POC_1.pdf, POC_3.pdf, etc.]
        PDF_MULTI[Multiple PDF Files<br/>Batch Processing]
        PDF_SCANNED[Scanned PDF Files<br/>Image-based Documents]
        BASE_EXCEL[Base Excel File<br/>consolidated_acss_invoices_sample_output.xlsx]
        CONFIG[Configuration Files<br/>.env, sap_schema.py]
    end
    
    subgraph INTL ["Interface Layer"]
        WEB_UI[Streamlit Web UI<br/>Single & Batch Support]
        CLI[Command Line Interface<br/>Batch Processing Scripts]
        API[Python API<br/>Programmatic Access]
    end
    
    subgraph PL ["Processing Layer"]
        ORCHESTRATOR[Orchestrator Agent<br/>Single & Batch Coordination]
        
        subgraph AP ["Agent Pipeline"]
            PDF_AGENT[PDF Agent<br/>pdfplumber + Textract Fallback]
            LLM_AGENT[LLM Agent<br/>3-Phase + Chunking + Batching]
            VAL_AGENT[Validation Agent<br/>Quality Assessment + Scoring]
            XLS_AGENT[Excel Agent<br/>Generation + Updates + Backups]
        end
    end
    
    subgraph ES ["External Services"]
        GROQ_API[Groq<br/>LLaMA 3.3 70B API<br/>Chunked Processing]
        AWS_TEXTRACT[AWS Textract<br/>OCR + Forms + Tables<br/>Scanned PDF Fallback]
    end
    
    subgraph UL ["Utility Layer"]
        DATE_UTILS[Date Utilities<br/>Parsing & Formatting]
        VAL_UTILS[Validation Utilities<br/>Data Cleaning & Validation]
        SAP_SCHEMA[SAP Schema<br/>35 Field Definitions + Defaults]
    end
    
    subgraph OL ["Output Layer"]
        RAW_JSON[Raw JSON Files<br/>raw_invoice_*.json<br/>batch_raw_invoices_*.json]
        SAP_JSON[SAP JSON Files<br/>sap_invoice_*.json<br/>batch_sap_invoices_*.json]
        EXCEL_FILES[Excel Files<br/>Updated or New<br/>invoice_output_*.xlsx]
        CONF_REPORTS[Confidence Reports<br/>confidence_report_*.json<br/>batch_processing_report_*.json]
        BACKUPS[Automatic Backups<br/>filename.backup_timestamp.xlsx]
    end
    
    subgraph SL ["Storage Layer"]
        OUTPUT_DIR[Output Directory<br/>Timestamped Files + Reports]
        TEMP_DIR[Temp Directory<br/>Uploaded Files]
    end
    
    PDF_SINGLE --> WEB_UI
    PDF_MULTI --> WEB_UI
    PDF_SCANNED --> WEB_UI
    PDF_SINGLE --> CLI
    PDF_MULTI --> CLI
    PDF_SINGLE --> API
    PDF_MULTI --> API
    BASE_EXCEL --> WEB_UI
    CONFIG --> ORCHESTRATOR
    
    WEB_UI --> ORCHESTRATOR
    CLI --> ORCHESTRATOR
    API --> ORCHESTRATOR
    
    ORCHESTRATOR --> PDF_AGENT
    ORCHESTRATOR --> LLM_AGENT
    ORCHESTRATOR --> VAL_AGENT
    ORCHESTRATOR --> XLS_AGENT
    
    LLM_AGENT <--> GROQ_API
    PDF_AGENT <--> AWS_TEXTRACT
    
    PDF_AGENT --> DATE_UTILS
    VAL_AGENT --> VAL_UTILS
    LLM_AGENT --> SAP_SCHEMA
    XLS_AGENT --> SAP_SCHEMA
    
    PDF_AGENT --> RAW_JSON
    LLM_AGENT --> SAP_JSON
    VAL_AGENT --> CONF_REPORTS
    XLS_AGENT --> EXCEL_FILES
    XLS_AGENT --> BACKUPS
    
    RAW_JSON --> OUTPUT_DIR
    SAP_JSON --> OUTPUT_DIR
    EXCEL_FILES --> OUTPUT_DIR
    CONF_REPORTS --> OUTPUT_DIR
    BACKUPS --> OUTPUT_DIR
    
    WEB_UI --> TEMP_DIR
    
    style ORCHESTRATOR fill:#e1f5fe
    style LLM_AGENT fill:#f3e5f5
    style GROQ_API fill:#fff3e0
    style AWS_TEXTRACT fill:#e8f5e8
    style OUTPUT_DIR fill:#e8f5e8
    style SAP_SCHEMA fill:#e3f2fd
    style BACKUPS fill:#fff3e0
```

---

## Summary

These enhanced flowcharts represent the complete current state of the SAP Invoice Processing System including:

1. **Multi-Agent Architecture** - 5 specialized agents with enhanced capabilities
2. **Batch Processing** - Multiple PDF support with combined outputs
3. **AWS Textract Fallback** - Automatic OCR for scanned documents
4. **Excel Update Functionality** - Direct file updates with automatic backups
5. **Large Document Handling** - Intelligent chunking and batch normalization
6. **Enhanced UI** - Single and multiple PDF upload modes
7. **Comprehensive Error Handling** - Graceful degradation and detailed reporting
8. **Complete Audit Trail** - All intermediate outputs and processing metadata
9. **Granular Line Item Extraction** - Each charge as separate line item
10. **System Integration** - All components working together seamlessly

Each flowchart uses Mermaid syntax and provides clear visual documentation of the system's enhanced architecture and processes, reflecting all recent improvements and current capabilities.