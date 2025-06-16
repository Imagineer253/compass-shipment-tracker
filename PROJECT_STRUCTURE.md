# COMPASS Project Structure

## Clean Architecture Overview

The COMPASS shipment management system has been restructured with a **clean separation of concerns** for better maintainability and organization.

## Directory Structure

```
COMPASS/
├── compass/
│   ├── static/
│   │   ├── css/                    # Dedicated CSS files (legacy, now embedded)
│   │   │   ├── export_shipment.css # Export form styling (now inline)
│   │   │   ├── import_shipment.css # Import form styling (future)
│   │   │   └── cold_shipment.css   # Cold shipment styling (future)
│   │   ├── js/                     # Dedicated JavaScript files (legacy, now embedded)
│   │   │   ├── export_shipment.js  # Export form functionality (now inline)
│   │   │   ├── import_shipment.js  # Import form functionality (future)
│   │   │   └── cold_shipment.js    # Cold shipment functionality (future)
│   │   └── images/                 # Static images
│   ├── templates/
│   │   ├── base.html               # Base template with Arctic theme
│   │   ├── shipments/              # Shipment templates with embedded CSS/JS
│   │   │   ├── export_shipment.html    # Working export form (embedded style)
│   │   │   ├── import_shipment.html    # Import form (embedded style)
│   │   │   ├── cold_shipment.html      # Cold shipment form
│   │   │   └── type_selection.html     # Shipment type selection
│   │   ├── dashboard/              # Dashboard templates
│   │   │   ├── admin_dashboard.html    # Admin interface
│   │   │   └── user_dashboard.html     # User interface
│   │   └── admin/                  # Admin specific templates
│   ├── models.py                   # Database models
│   ├── main.py                     # Route handlers with package type mapping
│   └── __init__.py                 # Flask app initialization
├── templates for reference/        # Original reference templates
├── requirements.txt               # Python dependencies
└── app.py                        # Application entry point
```

## Key Improvements

### 1. **Embedded CSS and JavaScript** (Current Working Solution)
- **Architecture**: CSS and JavaScript are embedded directly in HTML templates
- **Reason**: Tailwind CSS peer utilities require processing with HTML for radio button functionality
- **Benefits**: 
  - Functional radio button interactions
  - Proper Arctic theme color application
  - Working invoice number generation
  - Functional dynamic form generation

### 2. **Standardized Package Types**
- **New Package Types**: 
  1. Cardboard Box (📦)
  2. Plastic Crate (🗃️)
  3. Metal Trunk (🗳️)
  4. Zarges (🧳)
  5. Pelican Case (💼)
  6. Other (📝)
- **Backend Support**: `get_package_type_display_name()` function converts codes to display names
- **Legacy Compatibility**: Maintains backward compatibility with old package type values

### 3. **Arctic Theme Integration**
- **Color Variables**: Proper CSS variable system for Arctic colors
- **Visual Feedback**: Working radio button selections with visual indicators
- **Consistent Styling**: Unified Arctic theme across all components

### 4. **Simplified Backend**
- **Package Type Mapping**: Centralized function for package type display names
- **Removed Edit Functionality**: Clean CRUD operations without complex edit logic
- **Streamlined Document Generation**: Improved document creation with proper package type display
- **User Workflow**: Users create new shipments instead of editing existing ones for changes

### Package Type System
COMPASS now supports 6 standardized package types:
- 📦 Cardboard Box
- 🗃️ Plastic Crate  
- 🗳️ Metal Trunk
- 🧳 Zarges
- 💼 Pelican Case
- 📝 Other

The `get_package_type_display_name()` function handles conversion and legacy compatibility.

### Document Generation System
COMPASS supports two document types:
- **Invoice & Packing List** (`invoice_packinglist.docx`) - For basic shipping needs
- **Custom Documents** (`export_custom_docs.docx`) - For full customs clearance documentation

Both admin and user dashboards offer separate buttons for each document type.

### Combined Shipment System
COMPASS allows admins to combine multiple shipments of the same type and expedition year:

#### Invoice Number Format
- **Export**: `NCPOR/ARC/{year}/COMBINED/{batch}/Combined/{number}`
- **Import/Reimport**: `NCPOR/IMP/{year}/RESEARCH/{batch}/Combined/{number}`  
- **Cold**: `NCPOR/COLD/{year}/{batch}/Combined/{number}`

#### Combine Form Features
- **Editable Fields**: All shipment and item details are fully editable
- **Requester Mapping**: Original requester names populate item-level "Attn" fields
- **Dynamic Calculations**: Total values update automatically when quantity/unit value changes
- **Real-time Validation**: Form validates all required fields with visual feedback
- **Original Tracking**: Combined shipments reference parent shipment IDs

#### Workflow
1. Admin selects multiple compatible shipments
2. System generates unique combined invoice number using sequential counter
3. Combine form displays all items with original requester names pre-populated
4. Admin can edit any field including descriptions, quantities, values
5. System validates all required fields before document generation
6. Original shipments marked as "Combined"

The system maintains full traceability between combined and original shipments.

## File-by-File Details

### HTML Templates (`