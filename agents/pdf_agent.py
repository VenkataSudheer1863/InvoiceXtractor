"""PDF Extraction Agent"""
import pdfplumber
import boto3
import fitz  # PyMuPDF
import json
import os
from typing import Dict, Any, List
from datetime import datetime
from botocore.exceptions import ClientError
from .base_agent import BaseAgent

class PDFAgent(BaseAgent):
    """Agent responsible for extracting text and structure from PDF"""
    
    def __init__(self):
        super().__init__("PDFAgent")
        # Initialize AWS Textract client
        self.textract_client = None
        self._init_textract()
    
    def _init_textract(self):
        """Initialize AWS Textract client if credentials are available"""
        try:
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            aws_region = os.getenv('AWS_REGION', 'us-east-1')
            
            if aws_access_key and aws_secret_key:
                self.textract_client = boto3.client(
                    'textract',
                    region_name=aws_region,
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key
                )
                self.log_info("AWS Textract client initialized successfully")
            else:
                self.log_warning("AWS credentials not found - Textract fallback unavailable")
        except Exception as e:
            self.log_error(f"Failed to initialize AWS Textract: {str(e)}")
    def _extract_key_value_pairs(self, blocks):
        """Extract key-value pairs from Textract blocks with better mapping"""
        key_value_pairs = {}
        key_map = {}
        value_map = {}
        
        # First pass: build maps for keys and values
        for block in blocks:
            if block['BlockType'] == 'KEY_VALUE_SET':
                if 'KEY' in block.get('EntityTypes', []):
                    key_map[block['Id']] = block
                elif 'VALUE' in block.get('EntityTypes', []):
                    value_map[block['Id']] = block
        
        # Second pass: match keys with values
        for key_id, key_block in key_map.items():
            key_text = ""
            value_text = ""
            
            # Extract key text
            if 'Relationships' in key_block:
                for relationship in key_block['Relationships']:
                    if relationship['Type'] == 'CHILD':
                        for child_id in relationship['Ids']:
                            child_block = next((b for b in blocks if b['Id'] == child_id), None)
                            if child_block and child_block['BlockType'] == 'WORD':
                                key_text += child_block['Text'] + " "
            
            # Find corresponding value
            if 'Relationships' in key_block:
                for relationship in key_block['Relationships']:
                    if relationship['Type'] == 'VALUE':
                        for value_id in relationship['Ids']:
                            if value_id in value_map:
                                value_block = value_map[value_id]
                                if 'Relationships' in value_block:
                                    for val_relationship in value_block['Relationships']:
                                        if val_relationship['Type'] == 'CHILD':
                                            for child_id in val_relationship['Ids']:
                                                child_block = next((b for b in blocks if b['Id'] == child_id), None)
                                                if child_block and child_block['BlockType'] == 'WORD':
                                                    value_text += child_block['Text'] + " "
            
            if key_text.strip():
                # Clean up the key text
                clean_key = key_text.strip().replace(':', '').replace(' ', '_')
                key_value_pairs[clean_key] = value_text.strip()
        
        return key_value_pairs
    
    def _extract_tables(self, blocks):
        """Extract table data from Textract blocks - text only with better structure"""
        tables = []
        table_blocks = [block for block in blocks if block['BlockType'] == 'TABLE']
        
        for table_block in table_blocks:
            table_data = {
                'table_id': table_block['Id'],
                'rows': []
            }
            
            if 'Relationships' in table_block:
                for relationship in table_block['Relationships']:
                    if relationship['Type'] == 'CHILD':
                        cells = []
                        for cell_id in relationship['Ids']:
                            cell_block = next((b for b in blocks if b['Id'] == cell_id and b['BlockType'] == 'CELL'), None)
                            if cell_block:
                                cell_text = ""
                                if 'Relationships' in cell_block:
                                    for cell_relationship in cell_block['Relationships']:
                                        if cell_relationship['Type'] == 'CHILD':
                                            for word_id in cell_relationship['Ids']:
                                                word_block = next((b for b in blocks if b['Id'] == word_id), None)
                                                if word_block and word_block['BlockType'] == 'WORD':
                                                    cell_text += word_block['Text'] + " "
                                
                                cells.append({
                                    'row_index': cell_block.get('RowIndex', 0),
                                    'column_index': cell_block.get('ColumnIndex', 0),
                                    'text': cell_text.strip()
                                })
                        
                        # Group cells by row
                        rows = {}
                        for cell in cells:
                            row_idx = cell['row_index']
                            if row_idx not in rows:
                                rows[row_idx] = []
                            rows[row_idx].append(cell)
                        
                        # Sort and format rows
                        for row_idx in sorted(rows.keys()):
                            row_cells = sorted(rows[row_idx], key=lambda x: x['column_index'])
                            row_data = [cell['text'] for cell in row_cells]
                            # Only add rows that have content
                            if any(cell.strip() for cell in row_data):
                                table_data['rows'].append(row_data)
            
            # Only add tables that have content
            if table_data['rows']:
                tables.append(table_data)
        
        return tables
    
    def _extract_remaining_text(self, blocks, key_value_pairs, tables):
        """Extract text that's not part of key-value pairs or tables"""
        # Get all word IDs that are part of key-value pairs or tables
        used_word_ids = set()
        
        # Add word IDs from key-value pairs
        for block in blocks:
            if block['BlockType'] == 'KEY_VALUE_SET':
                if 'Relationships' in block:
                    for relationship in block['Relationships']:
                        if relationship['Type'] == 'CHILD':
                            used_word_ids.update(relationship['Ids'])
                        elif relationship['Type'] == 'VALUE':
                            for value_id in relationship['Ids']:
                                value_block = next((b for b in blocks if b['Id'] == value_id), None)
                                if value_block and 'Relationships' in value_block:
                                    for val_rel in value_block['Relationships']:
                                        if val_rel['Type'] == 'CHILD':
                                            used_word_ids.update(val_rel['Ids'])
        
        # Add word IDs from tables
        for block in blocks:
            if block['BlockType'] == 'TABLE':
                if 'Relationships' in block:
                    for relationship in block['Relationships']:
                        if relationship['Type'] == 'CHILD':
                            for cell_id in relationship['Ids']:
                                cell_block = next((b for b in blocks if b['Id'] == cell_id and b['BlockType'] == 'CELL'), None)
                                if cell_block and 'Relationships' in cell_block:
                                    for cell_rel in cell_block['Relationships']:
                                        if cell_rel['Type'] == 'CHILD':
                                            used_word_ids.update(cell_rel['Ids'])
        
        # Extract remaining text lines - only text, no coordinates
        remaining_lines = []
        for block in blocks:
            if block['BlockType'] == 'LINE':
                line_word_ids = set()
                if 'Relationships' in block:
                    for relationship in block['Relationships']:
                        if relationship['Type'] == 'CHILD':
                            line_word_ids.update(relationship['Ids'])
                
                # If this line has words not used in key-value pairs or tables
                if not line_word_ids.issubset(used_word_ids):
                    remaining_lines.append(block['Text'])
        
        return remaining_lines
    
    def _extract_with_textract(self, pdf_path):
        """Fallback extraction using AWS Textract for scanned/image PDFs"""
        if not self.textract_client:
            self.log_error("Textract client not available")
            return None
        
        self.log_info("Falling back to AWS Textract for scanned PDF processing")
        
        try:
            # Initialize result structure
            result = {
                'document_metadata': {
                    'source_file': pdf_path,
                    'processing_timestamp': datetime.now().isoformat(),
                    'total_pages': 0,
                    'processing_method': 'AWS Textract with Forms and Tables'
                },
                'pages': [],
                'summary': {
                    'total_key_value_pairs': 0,
                    'total_tables': 0,
                    'total_remaining_text_lines': 0
                }
            }
            
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(pdf_path)
            result['document_metadata']['total_pages'] = len(pdf_document)
            
            raw_text = ""
            pages = []
            all_tables = []
            
            for page_num in range(len(pdf_document)):
                self.log_info(f"Processing page {page_num + 1}/{len(pdf_document)} with Textract")
                
                # Get page
                page = pdf_document[page_num]
                
                # Convert page to image (PNG)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_data = pix.tobytes("png")
                
                page_result = {
                    'page_number': page_num + 1,
                    'processing_status': 'success',
                    'key_value_pairs': {},
                    'tables': [],
                    'remaining_text': []
                }
                
                try:
                    # Try analyze_document for tables and forms
                    response = self.textract_client.analyze_document(
                        Document={'Bytes': img_data},
                        FeatureTypes=["TABLES", "FORMS"]
                    )
                    
                    blocks = response.get('Blocks', [])
                    
                    # Extract key-value pairs
                    key_value_pairs = self._extract_key_value_pairs(blocks)
                    page_result['key_value_pairs'] = key_value_pairs
                    
                    # Extract tables
                    tables = self._extract_tables(blocks)
                    page_result['tables'] = tables
                    
                    # Extract remaining text
                    remaining_text = self._extract_remaining_text(blocks, key_value_pairs, tables)
                    page_result['remaining_text'] = remaining_text
                    
                    # Build page text for compatibility
                    page_text_parts = []
                    
                    # Add key-value pairs
                    for key, value in key_value_pairs.items():
                        page_text_parts.append(f"{key}: {value}")
                    
                    # Add table data
                    for table in tables:
                        for row in table['rows']:
                            page_text_parts.append(" | ".join(row))
                    
                    # Add remaining text
                    page_text_parts.extend(remaining_text)
                    
                    page_text = "\n".join(page_text_parts)
                    pages.append(page_text)
                    raw_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                    
                    # Convert Textract tables to pdfplumber format
                    for table in tables:
                        all_tables.append(table['rows'])
                    
                    # Update summary
                    result['summary']['total_key_value_pairs'] += len(key_value_pairs)
                    result['summary']['total_tables'] += len(tables)
                    result['summary']['total_remaining_text_lines'] += len(remaining_text)
                    
                    self.log_info(f"Page {page_num + 1}: {len(key_value_pairs)} key-value pairs, {len(tables)} tables, {len(remaining_text)} text lines")
                    
                except ClientError as e:
                    self.log_warning(f"Page {page_num + 1} failed with forms/tables, trying text detection: {e.response['Error']['Code']}")
                    page_result['processing_status'] = 'failed_fallback'
                    
                    # Fallback to simple text detection
                    try:
                        response = self.textract_client.detect_document_text(
                            Document={'Bytes': img_data}
                        )
                        blocks = response.get('Blocks', [])
                        
                        # For fallback, put all text in remaining_text
                        fallback_text = []
                        for block in blocks:
                            if block['BlockType'] == 'LINE':
                                fallback_text.append(block['Text'])
                        
                        page_result['remaining_text'] = fallback_text
                        page_text = "\n".join(fallback_text)
                        pages.append(page_text)
                        raw_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                        
                        result['summary']['total_remaining_text_lines'] += len(fallback_text)
                        self.log_info(f"Page {page_num + 1} fallback: {len(fallback_text)} text lines")
                        
                    except ClientError as fallback_error:
                        self.log_error(f"Page {page_num + 1} fallback also failed: {fallback_error}")
                        page_result['processing_status'] = 'failed'
                        page_result['error'] = str(fallback_error)
                        pages.append("")  # Add empty page to maintain page count
                
                result['pages'].append(page_result)
            
            pdf_document.close()
            
            # Log summary
            self.log_info(f"Textract processing complete: {len(result['pages'])} pages, "
                         f"{result['summary']['total_key_value_pairs']} key-value pairs, "
                         f"{result['summary']['total_tables']} tables, "
                         f"{result['summary']['total_remaining_text_lines']} text lines")
            
            # Return in the same format as pdfplumber
            return {
                "raw_text": raw_text.strip(),
                "pages": pages,
                "tables": all_tables,
                "metadata": {
                    "num_pages": len(pages),
                    "num_tables": len(all_tables),
                    "processing_method": "AWS Textract",
                    "textract_details": result
                },
                "status": "success"
            }
            
        except Exception as e:
            self.log_error(f"Textract processing failed: {str(e)}")
            return None
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract text from PDF with Textract fallback for scanned documents
        
        Args:
            input_data: {"pdf_path": str}
        
        Returns:
            {
                "raw_text": str,
                "pages": List[str],
                "tables": List[List[List[str]]],
                "metadata": Dict
            }
        """
        pdf_path = input_data.get("pdf_path")
        
        if not pdf_path:
            self.log_error("No PDF path provided")
            return {"error": "No PDF path provided"}
        
        try:
            self.log_info(f"Extracting text from {pdf_path}")
            
            # First, try pdfplumber extraction
            with pdfplumber.open(pdf_path) as pdf:
                raw_text = ""
                pages = []
                tables = []
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text() or ""
                    pages.append(page_text)
                    raw_text += f"\n--- Page {page_num} ---\n{page_text}"
                    
                    # Extract tables if present
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
                
                # Check if extraction was successful (has meaningful content)
                total_text_length = sum(len(page.strip()) for page in pages)
                
                if total_text_length < 100:  # Threshold for minimal content
                    self.log_warning(f"PDFPlumber extracted minimal content ({total_text_length} chars). "
                                   "This might be a scanned PDF. Attempting Textract fallback...")
                    
                    # Try Textract fallback
                    textract_result = self._extract_with_textract(pdf_path)
                    if textract_result:
                        self.log_info("Successfully extracted content using Textract fallback")
                        return textract_result
                    else:
                        self.log_warning("Textract fallback failed, returning pdfplumber results")
                
                metadata = {
                    "num_pages": len(pdf.pages),
                    "num_tables": len(tables),
                    "processing_method": "PDFPlumber"
                }
                
                self.log_info(f"Extracted {len(pdf.pages)} pages, {len(tables)} tables using PDFPlumber")
                
                return {
                    "raw_text": raw_text.strip(),
                    "pages": pages,
                    "tables": tables,
                    "metadata": metadata,
                    "status": "success"
                }
        
        except Exception as e:
            self.log_error(f"PDFPlumber extraction failed: {str(e)}")
            
            # If pdfplumber fails completely, try Textract as fallback
            if self.textract_client:
                self.log_info("PDFPlumber failed completely, attempting Textract fallback...")
                textract_result = self._extract_with_textract(pdf_path)
                if textract_result:
                    self.log_info("Successfully recovered using Textract fallback")
                    return textract_result
            
            self.log_error("All extraction methods failed")
            return {"error": str(e), "status": "failed"}
