# Template Setup Instructions

## What the Code Changes Do

The COMPASS system has been updated to support two different types of document generation:

1. **Invoice & Packing List** (`invoice_packinglist.docx`) - For basic shipping needs
2. **Custom Documents** (`export_custom_docs.docx`) - For full customs clearance documentation

## Manual File Operations Required

You mentioned you'll handle the file operations manually. Here's what needs to be done in the `templates/` directory:

### Step 1: Rename the Current Template
```bash
# Navigate to the templates directory
cd templates/

# Rename the current export.docx to invoice_packinglist.docx
mv export.docx invoice_packinglist.docx
```

### Step 2: Create the Custom Documents Template
```bash
# Create a copy for custom documents
cp invoice_packinglist.docx export_custom_docs.docx
```

### Final Template Structure
After these operations, your `templates/` directory should contain:
- `invoice_packinglist.docx` - For invoice & packing list generation
- `export_custom_docs.docx` - For full customs clearance documents

## What the Code Updates Include

### Backend Changes (`compass/main.py`):
- ✅ Updated `generate_shipment_document()` function to accept `document_type` parameter
- ✅ Modified admin and user document generation routes to support both document types
- ✅ Added template path selection logic based on document type
- ✅ Updated filename generation to reflect document type

### Frontend Changes:
- ✅ **Admin Dashboard**: Replaced single "Generate Document" button with two buttons:
  - "📄 Invoice & Packing" (green button)
  - "📋 Custom Docs" (blue button)
- ✅ **User Dashboard**: Replaced single "Download Documents" button with two buttons:
  - "📄 Invoice & Packing" (green button) 
  - "📋 Custom Docs" (blue button)

### Route Updates:
- ✅ `/admin/generate-document/<shipment_id>/<document_type>` - Admin document generation
- ✅ `/user/generate-document/<shipment_id>/<document_type>` - User document generation
- ✅ Both routes default to `invoice_packing` if no document type specified

## How It Works

1. **For Invoice & Packing List**: 
   - Uses `invoice_packinglist.docx` template
   - Generates files with `_invoice_packing_` in filename
   - Green buttons in UI

2. **For Custom Documents**:
   - Uses `export_custom_docs.docx` template  
   - Generates files with `_custom_docs_` in filename
   - Blue buttons in UI

## Testing After File Operations

Once you've completed the manual file operations:

1. Start the application: `python app.py`
2. Navigate to admin or user dashboard
3. You should see two document generation buttons for each shipment
4. Test both document types to ensure they generate correctly

## Notes

- The `export_custom_docs.docx` template can be customized later for additional customs documentation
- Both templates use the same data structure, so existing shipments will work with both document types
- Combined shipments default to "Invoice & Packing" document type
- All existing functionality remains intact 