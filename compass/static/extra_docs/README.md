# Extra Documents for COMPASS Shipments

This folder contains additional documents that are automatically appended to generated shipment documents.

## Folder Structure

- `normal_temp_import/` - Extra documents for Normal Temperature Sample Import shipments
  - Place PDF files here that should be appended to the end of normal temp import documents
  - Files will be appended in alphabetical order
  - Supported formats: PDF

## Usage

1. Place your additional PDF documents in the appropriate subfolder
2. When generating documents for the corresponding shipment type, these will be automatically appended
3. Files are appended in alphabetical order, so use prefixes like `01_`, `02_`, etc. to control order

## Example

For Normal Temperature Sample Import:
```
normal_temp_import/
├── 01_safety_guidelines.pdf
├── 02_handling_instructions.pdf
└── 03_compliance_checklist.pdf
```

These will be appended to the main document in this order.
