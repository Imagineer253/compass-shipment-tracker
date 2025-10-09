# PDF Generation and Extra Documents Guide

## Overview

The COMPASS system now supports generating documents in both DOCX and PDF formats. For certain shipment types, additional documents can be automatically appended to the PDF output.

## Features

### 1. PDF Document Generation
- Convert DOCX documents to PDF format
- Maintain all formatting and content from the original DOCX
- Support for both Invoice & Packing List and Custom Documents

### 2. Extra Documents Appending
- Automatically append additional PDF documents to the main document
- Currently configured for Normal Temperature Sample Import shipments
- Documents are appended in alphabetical order

### 3. User Interface Updates
- New PDF buttons in both Admin and User dashboards
- Clear distinction between DOCX and PDF options
- Tooltips indicating when extra documents will be included

## How to Use

### Admin Dashboard
1. Navigate to the Admin Dashboard
2. Find the shipment you want to generate documents for
3. In the Actions column, you'll see new buttons:
   - 📑 (Red) - Generate Invoice & Packing PDF with extras
   - 📕 (Indigo) - Generate Custom Docs PDF with extras
   - 📄 (Green) - Generate Invoice & Packing DOCX (original)
   - 📋 (Blue) - Generate Custom Docs DOCX (original)

### User Dashboard
1. Navigate to your User Dashboard
2. Find a shipment with "Awaiting Quotation Approval" status
3. You'll see two sections:
   - **📄 DOCX Documents** - Original Word format
   - **📑 PDF Documents (with Extra Pages)** - PDF with additional documents

## Extra Documents Configuration

### Current Setup
For **Normal Temperature Sample Import** shipments, the following extra documents are automatically appended:

1. **01_safety_guidelines.pdf** - Safety requirements and procedures
2. **02_handling_instructions.pdf** - Detailed handling and processing guidelines
3. **03_compliance_checklist.pdf** - Regulatory compliance requirements

### Adding New Extra Documents

To add new extra documents:

1. Navigate to `compass/static/extra_docs/normal_temp_import/`
2. Add your PDF files with appropriate naming (e.g., `04_new_document.pdf`)
3. Files are automatically included in alphabetical order
4. Use number prefixes to control the order

### Adding Extra Documents for Other Shipment Types

To add extra documents for other shipment types:

1. Create a new folder in `compass/static/extra_docs/`
2. Update the `get_extra_documents()` function in `compass/utils/pdf_utils.py`
3. Add the logic for your new shipment type

Example:
```python
elif shipment_type == 'export' and temperature_type == 'cold':
    docs_folder = Path(__file__).parent.parent / 'static' / 'extra_docs' / 'cold_export'
```

## Technical Details

### PDF Conversion Methods
The system uses multiple fallback methods for PDF conversion:

1. **docx2pdf** - Primary method (Windows with Word installed)
2. **LibreOffice** - Secondary method (Linux/macOS)
3. **Error PDF** - Fallback method (creates a simple PDF with error message)

### PDF Merging
- Uses PyPDF2 for merging multiple PDF files
- Maintains page order and formatting
- Handles errors gracefully with fallback options

### File Naming
PDF files follow the same naming convention as DOCX files but with `.pdf` extension:
- Format: `requester_first_name_Type_of_Shipment_month_document_series_number.pdf`
- Example: `John_SAM_IMP_RT_October_001.pdf`

## Routes and Endpoints

### Admin Routes
- `/admin/generate-pdf/<shipment_id>` - Generate PDF with invoice_packing type
- `/admin/generate-pdf/<shipment_id>/<document_type>` - Generate PDF with specified type

### User Routes
- `/user/generate-pdf/<shipment_id>` - Generate PDF with invoice_packing type
- `/user/generate-pdf/<shipment_id>/<document_type>` - Generate PDF with specified type

## Dependencies

The following Python packages are required:
- `PyPDF2==3.0.1` - PDF manipulation
- `reportlab==4.0.4` - PDF creation
- `docx2pdf==0.1.8` - DOCX to PDF conversion

## Troubleshooting

### PDF Conversion Issues
1. **Windows**: Ensure Microsoft Word is installed for docx2pdf
2. **Linux/macOS**: Install LibreOffice for conversion
3. **Fallback**: System will create an error PDF if conversion fails

### Missing Extra Documents
1. Check that PDF files exist in the correct folder
2. Verify file permissions allow reading
3. Check the `get_extra_documents()` function logic

### Performance Considerations
- PDF generation may take longer than DOCX generation
- Large extra documents will increase processing time
- Consider file size limits for web downloads

## Security Notes

- Extra documents are served from the static folder
- Only PDF files are processed for merging
- File paths are validated to prevent directory traversal
- Temporary files are cleaned up after processing

## Future Enhancements

Potential improvements:
1. Admin interface for managing extra documents
2. Per-shipment custom extra documents
3. Watermarking and digital signatures
4. Batch PDF generation
5. Email delivery of PDF documents
