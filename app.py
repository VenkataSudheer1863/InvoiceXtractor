"""Streamlit UI for Invoice Processing System"""
import streamlit as st
import os
import json
import pandas as pd
import time
from agents.orchestrator import OrchestratorAgent
from datetime import datetime

# Page config
st.set_page_config(
    page_title="InvoiceXtractor",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False
if "result" not in st.session_state:
    st.session_state.result = None
if "execution_time" not in st.session_state:
    st.session_state.execution_time = None

# Title
st.title("📄InvoiceXtractor")
st.markdown("Upload a PDF invoice to automatically extract and populate SAP Excel format")

# Sidebar
with st.sidebar:
    # Replace st.header("⚙️ Configuration") with this:
    base_excel_path = st.text_input(
        "Base Excel File Path",
        value="consolidated_acss_invoices_sample_output.xlsx",
        help="Path to existing Excel file to append to"
    )
    
    output_dir = st.text_input(
        "Output Directory",
        value="output",
        help="Directory to save output files"
    )
    
    st.markdown("---")
    st.markdown("### 🤖 Agent Pipeline")
    st.markdown("""
    1. **PDF Agent**: Extract text
    2. **LLM Agent**: Detect & extract
    3. **LLM Agent**: Normalize to SAP
    4. **Validation Agent**: Validate data
    5. **Excel Agent**: Generate Excel
    """)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload Invoice(s)")
    
    # Option to upload single or multiple files
    upload_mode = st.radio(
        "Upload Mode",
        ["Single PDF", "Multiple PDFs"],
        horizontal=True
    )
    
    if upload_mode == "Single PDF":
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Upload a text-based PDF invoice"
        )
        uploaded_files = [uploaded_file] if uploaded_file else []
    else:
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload multiple text-based PDF invoices"
        )
        if not uploaded_files:
            uploaded_files = []
    
    if uploaded_files:
        # Save uploaded files temporarily
        temp_pdf_paths = []
        os.makedirs("temp", exist_ok=True)
        
        for uploaded_file in uploaded_files:
            temp_pdf_path = os.path.join("temp", uploaded_file.name)
            with open(temp_pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            temp_pdf_paths.append(temp_pdf_path)
        
        if len(uploaded_files) == 1:
            st.success(f"✅ Uploaded: {uploaded_files[0].name}")
        else:
            st.success(f"✅ Uploaded {len(uploaded_files)} files:")
            for file in uploaded_files:
                st.write(f"  • {file.name}")
        
        # Process button
        process_label = "🚀 Process Invoice" if len(uploaded_files) == 1 else f"🚀 Process {len(uploaded_files)} Invoices"
        if st.button(process_label, type="primary", use_container_width=True):
            with st.spinner("Processing invoice(s)... This may take a few minutes for multiple files."):
                # Start timing
                start_time = time.time()
                
                # Initialize orchestrator
                orchestrator = OrchestratorAgent()
                
                # Execute pipeline
                if len(temp_pdf_paths) == 1:
                    # Single file processing
                    result = orchestrator.execute({
                        "pdf_path": temp_pdf_paths[0],
                        "base_excel_path": base_excel_path,
                        "output_dir": output_dir
                    })
                else:
                    # Multiple file processing
                    result = orchestrator.execute({
                        "pdf_paths": temp_pdf_paths,
                        "base_excel_path": base_excel_path,
                        "output_dir": output_dir
                    })
                
                # End timing
                end_time = time.time()
                execution_time = end_time - start_time
                
                st.session_state.result = result
                st.session_state.execution_time = execution_time
                st.session_state.processing_complete = True
            
            # Clean up temp files
            for temp_path in temp_pdf_paths:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

with col2:
    st.header("📊 Processing Status")
    
    if st.session_state.processing_complete and st.session_state.result:
        result = st.session_state.result
        
        if result.get("status") == "success":
            st.success("✅ Processing completed successfully!")
            
            # Display execution time
            # if st.session_state.execution_time is not None:
            #     execution_time = st.session_state.execution_time
            #     if execution_time < 60:
            #         time_display = f"⏱️ **Execution Time:** {execution_time:.2f} seconds"
            #     else:
            #         minutes = int(execution_time // 60)
            #         seconds = execution_time % 60
            #         time_display = f"⏱️ **Execution Time:** {minutes}m {seconds:.2f}s"
            #     st.info(time_display)
            
            # # Confidence score
            # confidence = result.get("confidence_score", 0)
            # st.metric("Confidence Score", f"{confidence:.1%}")
            
            # Validation report
            val_report = result.get("validation_report", {})
            excel_operation = result.get("excel_operation", "unknown")
            
            # Check if this is batch processing
            is_batch = "processed_files" in result or "total_files" in result
            
            if is_batch:
                col_a, col_b, col_c, col_d, col_e = st.columns(5)
                with col_a:
                    st.metric("Files Processed", f"{result.get('processed_files', 0)}/{result.get('total_files', 0)}")
                with col_b:
                    st.metric("Invoices", val_report.get("total_invoices", 0))
                with col_c:
                    st.metric("Line Items", val_report.get("total_line_items", 0))
                with col_d:
                    st.metric("Rows Added", result.get("num_rows_added", 0))
                with col_e:
                    operation_display = {
                        "updated": "📝 Updated",
                        "created": "🆕 Created", 
                        "created_from_template": "📋 From Template"
                    }.get(excel_operation, excel_operation)
                    st.metric("Excel Operation", operation_display)
                
                # Show execution time for batch processing
                # if st.session_state.execution_time is not None:
                #     execution_time = st.session_state.execution_time
                #     total_files = result.get('total_files', 1)
                #     avg_time_per_file = execution_time / total_files if total_files > 0 else execution_time
                #     
                #     col_time1, col_time2 = st.columns(2)
                #     with col_time1:
                #         if execution_time < 60:
                #             st.metric("Total Time", f"{execution_time:.1f}s")
                #         else:
                #             minutes = int(execution_time // 60)
                #             seconds = execution_time % 60
                #             st.metric("Total Time", f"{minutes}m {seconds:.0f}s")
                #     with col_time2:
                #         st.metric("Avg per File", f"{avg_time_per_file:.1f}s")
                
                # Show failed files if any
                failed_files = result.get("failed_files", 0)
                if failed_files > 0:
                    st.warning(f"⚠️ {failed_files} file(s) failed to process. Check batch report for details.")
            else:
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Invoices", val_report.get("total_invoices", 0))
                with col_b:
                    st.metric("Line Items", val_report.get("total_line_items", 0))
                with col_c:
                    st.metric("Rows Added", result.get("num_rows_added", 0))
                with col_d:
                    operation_display = {
                        "updated": "📝 Updated",
                        "created": "🆕 Created", 
                        "created_from_template": "📋 From Template"
                    }.get(excel_operation, excel_operation)
                    st.metric("Excel Operation", operation_display)
                
                # Show execution time for single file processing
                # if st.session_state.execution_time is not None:
                #     execution_time = st.session_state.execution_time
                #     if execution_time < 60:
                #         st.metric("⏱️ Processing Time", f"{execution_time:.2f} seconds")
                #     else:
                #         minutes = int(execution_time // 60)
                #         seconds = execution_time % 60
                #         st.metric("⏱️ Processing Time", f"{minutes}m {seconds:.1f}s")
            
            # Show backup info if file was updated
            if result.get("backup_created", False):
                st.info("💾 Backup created before updating existing Excel file")
            
            # Show total rows info
            total_rows = result.get("total_rows", 0)
            existing_rows = result.get("existing_rows", 0)
            if total_rows > 0:
                st.success(f"📊 Excel file now contains {total_rows} total rows ({existing_rows} existing + {result.get('num_rows_added', 0)} new)")
            
            # # Issues and warnings
            # issues = result.get("issues", [])
            # warnings = result.get("warnings", [])
            
            # if issues:
            #     with st.expander("⚠️ Issues", expanded=True):
            #         for issue in issues:
            #             st.warning(issue)
            
            # if warnings:
            #     with st.expander("⚡ Warnings"):
            #         for warning in warnings:
            #             st.info(warning)
            
        else:
            st.error("❌ Processing failed")
            st.error(result.get("error", "Unknown error"))

# Results section
if st.session_state.processing_complete and st.session_state.result:
    result = st.session_state.result
    
    if result.get("status") == "success":
        st.markdown("---")
        st.header("📋 Results")
        
        # Tabs for different outputs
        is_batch = "processed_files" in result or "total_files" in result
        
        if is_batch:
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 New Rows", "📄 Raw JSON", "🔄 SAP JSON", "📋 Batch Report", "📥 Downloads"])
        else:
            tab1, tab2, tab3, tab4 = st.tabs(["📊 New Rows", "📄 Raw JSON", "🔄 SAP JSON", "📥 Downloads"])
        
        with tab1:
            st.subheader("New Rows to be Added")
            new_rows = result.get("new_rows", [])
            
            if new_rows:
                df = pd.DataFrame(new_rows)
                st.dataframe(df, use_container_width=True, height=400)
                
                # Download as CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"new_rows_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No new rows generated")
        
        with tab2:
            st.subheader("Raw Extracted JSON")
            raw_json_path = result.get("raw_json_path")
            
            if raw_json_path and os.path.exists(raw_json_path):
                with open(raw_json_path, "r", encoding="utf-8") as f:
                    raw_json = json.load(f)
                
                st.json(raw_json)
                
                with open(raw_json_path, "r", encoding="utf-8") as f:
                    st.download_button(
                        label="📥 Download Raw JSON",
                        data=f.read(),
                        file_name=os.path.basename(raw_json_path),
                        mime="application/json"
                    )
        
        with tab3:
            st.subheader("SAP Normalized JSON")
            sap_json_path = result.get("sap_json_path")
            
            if sap_json_path and os.path.exists(sap_json_path):
                with open(sap_json_path, "r", encoding="utf-8") as f:
                    sap_json = json.load(f)
                
                st.json(sap_json)
                
                with open(sap_json_path, "r", encoding="utf-8") as f:
                    st.download_button(
                        label="📥 Download SAP JSON",
                        data=f.read(),
                        file_name=os.path.basename(sap_json_path),
                        mime="application/json"
                    )
        
        if is_batch:
            with tab4:
                st.subheader("Batch Processing Report")
                batch_report_path = result.get("batch_report_path")
                
                if batch_report_path and os.path.exists(batch_report_path):
                    with open(batch_report_path, "r", encoding="utf-8") as f:
                        batch_report = json.load(f)
                    
                    # Show summary
                    summary = batch_report.get("summary", {})
                    st.json(summary)
                    
                    # Show file details
                    if "processed_files" in batch_report and batch_report["processed_files"]:
                        st.subheader("✅ Successfully Processed Files")
                        for file_path in batch_report["processed_files"]:
                            st.write(f"• {os.path.basename(file_path)}")
                    
                    if "failed_files" in batch_report and batch_report["failed_files"]:
                        st.subheader("❌ Failed Files")
                        for failed_file in batch_report["failed_files"]:
                            st.write(f"• {os.path.basename(failed_file['file'])}: {failed_file['error']}")
                    
                    # Download batch report
                    with open(batch_report_path, "r", encoding="utf-8") as f:
                        st.download_button(
                            label="📥 Download Batch Report",
                            data=f.read(),
                            file_name=os.path.basename(batch_report_path),
                            mime="application/json"
                        )
        
        with tab4 if not is_batch else tab5:
            st.subheader("Download Files")
            
            excel_path = result.get("excel_path")
            # confidence_path = result.get("confidence_report_path")
            
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                if excel_path and os.path.exists(excel_path):
                    with open(excel_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Excel File",
                            data=f.read(),
                            file_name=os.path.basename(excel_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
            
            # with col_d2:
            #     if confidence_path and os.path.exists(confidence_path):
            #         with open(confidence_path, "r", encoding="utf-8") as f:
            #             st.download_button(
            #                 label="📥 Download Confidence Report",
            #                 data=f.read(),
            #                 file_name=os.path.basename(confidence_path),
            #                 mime="application/json",
            #                 use_container_width=True
            #             )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>SAP Invoice Processing System | Multi-Agent Architecture</p>
    <p>PDF Agent → LLM Agent → Validation Agent → Excel Agent</p>
</div>
""", unsafe_allow_html=True)
