# Testing Combined Export Functionality

This guide explains how to test the new combined export shipment functionality in COMPASS.

## Quick Start

### 1. Create Test Data
Run the test data creation script:
```bash
python scripts/create_test_combined_exports.py
```

This creates:
- 3 test users (Alice Johnson, Bob Smith, Carol Davis)
- 3 test export shipments (2 packages each, 6 total packages)
- All shipments are ready for combining

### 2. View Current Test Data
Run the debug script to see available shipments:
```bash
python scripts/test_combine_debug.py
```

This shows:
- All available test shipments
- Simulation of what combining them would look like
- Expected combined invoice number format

## Testing Methods

### Method 1: Debug Button (Quick Access)
1. Start the Flask app: `python app.py`
2. Login as admin
3. Go to Admin Dashboard
4. Click the red **"🧪 DEBUG: Test Combine Form"** button
5. The system will auto-select available test shipments

### Method 2: Manual Selection (Production Method)
1. Start the Flask app: `python app.py`
2. Login as admin
3. Go to Admin Dashboard
4. Select the test shipments using checkboxes
5. Click **"🔄 Combine Selected"** button

### Method 3: Direct URL Access
Navigate directly to: `http://localhost:5000/admin/combine-form`
- Auto-selects available test shipments for debugging

## What to Test

### 1. Combined Invoice Format
Expected format: `NCPOR/ARC/YYYY/MMM/EXP/TYPE/CMB/UNIQUE_IDS/SERIAL`

Example: `NCPOR/ARC/2025/JUN/EXP/RET/CMB/AL1CE1/BOB2SM/CAR0LD/0016`

Where:
- `RET` = Return type (determined from the shipments being combined)
- `CMB` = Combined indicator (same as real-time method)
- `AL1CE1/BOB2SM/CAR0LD` = Unique IDs of all users being combined
- `0016` = Sequential serial number

### 2. Package Limits
- **Individual exports**: 10 packages max
- **Combined exports**: 20 packages max
- Test shipments have 6 total packages (within limit)

### 3. Form Features
- **User dropdowns**: Each package item has dropdown to select attention person
- **Arctic theme**: Orange accents for combined shipments
- **Dynamic updates**: Transport mode changes update related fields
- **Form validation**: Prevents submission with invalid data

### 4. Document Generation
After creating combined shipment:
- Generate Invoice & Packing List
- Generate Custom Documents
- Check that all unique IDs are properly included
- Verify CMB indicator in invoice number

## Test Data Details

### Test Users Created
```
Alice Johnson (AL1CE1) - researcher1@ncpor.gov.in
Bob Smith (BOB2SM) - researcher2@ncpor.gov.in  
Carol Davis (CAR0LD) - researcher3@ncpor.gov.in
Password for all: test123
```

### Test Shipments Created
```
NCPOR/ARC/2025/JUN/EXP/RET/AL1CE1/0013 - Alice Johnson (2 packages)
NCPOR/ARC/2025/JUN/EXP/RET/BOB2SM/0014 - Bob Smith (2 packages)
NCPOR/ARC/2025/JUN/EXP/RET/CAR0LD/0015 - Carol Davis (2 packages)
```

## Expected Combined Result
```
Invoice: NCPOR/ARC/2025/JUN/EXP/RET/CMB/AL1CE1/BOB2SM/CAR0LD/0016
Total Packages: 6 (within 20 limit)
Status: Combined export ready for document generation
```

## Cleanup

### Remove Debug Button
After testing, remove the debug button from admin dashboard:
1. Edit `compass/templates/dashboard/admin_dashboard.html`
2. Remove the section marked with `<!-- TEMPORARY DEBUG LINK - REMOVE LATER -->`

### Remove Test Data (Optional)
The test data won't interfere with production, but you can remove it:
1. Delete test users from admin panel
2. Delete test shipments from admin panel
3. Or reset the database if needed

## Troubleshooting

### No Shipments Available
If you see "No shipments available for combining":
1. Run `python scripts/create_test_combined_exports.py` again
2. Check that shipments have status "Submitted" and are not already combined
3. Use `python scripts/test_combine_debug.py` to verify data

### Debug Button Not Showing
1. Make sure you're logged in as admin
2. Check that the debug button was added to the admin dashboard template
3. Refresh the browser page

### Form Errors
1. Check browser console for JavaScript errors
2. Verify all required fields are filled
3. Ensure package count doesn't exceed 20
4. Check that at least 2 shipments are selected

## Production Considerations

1. **Remove debug features** before production deployment
2. **Test with real data** to ensure compatibility
3. **Verify document templates** work with combined data
4. **Test package limits** with various combinations
5. **Validate user permissions** for combining functionality

---

**Note**: This is a testing environment setup. Remove all debug features and test data before production deployment. 