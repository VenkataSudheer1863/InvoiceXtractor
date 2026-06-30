# Excel Update Functionality

## Overview

The system now supports updating existing Excel files instead of always creating new timestamped files. This allows for continuous accumulation of invoice data in a single Excel file.

## How It Works

### Previous Behavior
- Always created new Excel files with timestamps: `invoice_output_20250203_123456.xlsx`
- Base Excel file was used only as a template
- Each processing run created a separate output file

### New Behavior
- **If base Excel path is specified and exists**: Updates the existing file directly
- **If base Excel path doesn't exist**: Creates new file with timestamp
- **Automatic backup creation** before updating existing files
- **Consistent output format** regardless of operation type

## Configuration

### Orchestrator Input
```python
orchestrator.execute({
    "pdf_path": "invoice.pdf",
    "base_excel_path": "consolidated_invoices.xlsx",  # File to update
    "output_dir": "output"
})
```

### Behavior Logic
```
If base_excel_path exists:
    excel_output_path = base_excel_path  # Update existing file
    Create backup before updating
Else:
    excel_output_path = output_dir/invoice_output_{timestamp}.xlsx  # New file
```

## Excel Agent Operations

### Operation Types
1. **"updated"**: Existing file updated directly (base_path == output_path)
2. **"created_from_template"**: New file created using existing file as template
3. **"created"**: New file created from scratch

### Backup System
- **Automatic backup** when updating existing files
- **Backup naming**: `{original_file}.backup_{timestamp}.xlsx`
- **Example**: `invoices.xlsx.backup_20250203_143022.xlsx`

### Safety Features
- Backup creation before any updates
- Path validation and existence checks
- Detailed logging of all operations
- Error handling with graceful fallbacks

## Output Information

### Enhanced Return Data
```python
{
    "excel_path": str,              # Path to final Excel file
    "excel_operation": str,         # "updated", "created", or "created_from_template"
    "num_rows_added": int,          # Number of new rows added
    "total_rows": int,              # Total rows in final file
    "existing_rows": int,           # Rows that existed before processing
    "backup_created": bool,         # Whether backup was created
    "status": "success"
}
```

### UI Display
- Shows operation type (Updated/Created/From Template)
- Displays row counts (existing + new = total)
- Indicates when backups are created
- Provides download links for updated files

## Usage Examples

### Example 1: Update Existing File
```python
# File exists: consolidated_invoices.xlsx (100 rows)
result = orchestrator.execute({
    "pdf_path": "new_invoice.pdf",
    "base_excel_path": "consolidated_invoices.xlsx"
})

# Result:
# - excel_path: "consolidated_invoices.xlsx"
# - excel_operation: "updated"
# - existing_rows: 100
# - num_rows_added: 5
# - total_rows: 105
# - backup_created: True
# - Backup file: "consolidated_invoices.xlsx.backup_20250203_143022.xlsx"
```

### Example 2: Create New File
```python
# File doesn't exist: missing_file.xlsx
result = orchestrator.execute({
    "pdf_path": "new_invoice.pdf", 
    "base_excel_path": "missing_file.xlsx",
    "output_dir": "output"
})

# Result:
# - excel_path: "output/invoice_output_20250203_143022.xlsx"
# - excel_operation: "created"
# - existing_rows: 0
# - num_rows_added: 5
# - total_rows: 5
# - backup_created: False
```

## Benefits

### Data Continuity
- **Single consolidated file** for all processed invoices
- **No manual file merging** required
- **Chronological data accumulation**

### Safety & Reliability
- **Automatic backups** prevent data loss
- **Atomic operations** ensure data integrity
- **Detailed logging** for audit trails

### Workflow Efficiency
- **Reduced file management** overhead
- **Consistent file locations** for downstream processes
- **Preserved existing functionality** for legacy workflows

## Migration Notes

### Existing Workflows
- **No breaking changes** to existing code
- **Backward compatible** with current implementations
- **Optional feature** - defaults to previous behavior if not configured

### Configuration Updates
- Update `base_excel_path` in UI or configuration files
- Ensure proper file permissions for backup creation
- Consider disk space for backup files

## Error Handling

### Common Scenarios
- **File locked**: Graceful error with retry suggestions
- **Permission denied**: Clear error message with resolution steps
- **Disk space**: Warning before backup creation
- **Corrupted Excel**: Fallback to new file creation

### Recovery Options
- **Backup restoration** from automatically created backups
- **Manual file recovery** using timestamped output files
- **Partial processing** with detailed error reports