#!/usr/bin/env python3
"""
Debug script to test combined shipment functionality
Run this from the project root directory: python scripts/test_combine_debug.py
"""

import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compass import create_app, db
from compass.models import User, Shipment, ShipmentSerialCounter

def list_test_shipments():
    """List all test shipments available for combining"""
    print("📋 Available test shipments for combining:")
    print("-" * 80)
    
    # Get all submitted export shipments
    shipments = Shipment.query.filter_by(
        shipment_type='export',
        status='Submitted'
    ).filter(
        Shipment.is_combined == False
    ).order_by(Shipment.created_at.desc()).all()
    
    if not shipments:
        print("❌ No suitable shipments found for combining!")
        print("   Run 'python scripts/create_test_combined_exports.py' first")
        return []
    
    for i, shipment in enumerate(shipments, 1):
        user = shipment.created_by_user
        print(f"{i:2d}. {shipment.invoice_number}")
        print(f"    Requester: {shipment.requester_name}")
        print(f"    User: {user.first_name} {user.last_name} ({user.unique_id})")
        print(f"    Packages: {shipment.total_packages}")
        print(f"    Status: {shipment.status}")
        print(f"    Created: {shipment.created_at.strftime('%Y-%m-%d %H:%M')}")
        print()
    
    return shipments

def simulate_combine_process(shipment_ids):
    """Simulate the combine process to show what would happen"""
    if not shipment_ids:
        print("❌ No shipments selected for combining")
        return
    
    print(f"🔄 Simulating combine process for {len(shipment_ids)} shipments...")
    print("-" * 60)
    
    # Get shipments
    shipments = Shipment.query.filter(Shipment.id.in_(shipment_ids)).all()
    
    if len(shipments) != len(shipment_ids):
        print("❌ Some shipments not found!")
        return
    
    # Calculate combined data
    total_packages = sum(s.total_packages for s in shipments)
    unique_ids = [s.created_by_user.unique_id for s in shipments]
    
    # Get next serial number (simulation)
    next_serial = ShipmentSerialCounter.get_next_serial()
    
    # Generate combined invoice number
    first_shipment = shipments[0]
    form_data = json.loads(first_shipment.form_data)
    
    from datetime import datetime
    current_date = datetime.now()
    year = current_date.strftime('%Y')
    month = current_date.strftime('%b').upper()
    
    # Extract return type from ALL shipments being combined to determine the type
    return_types = set()
    for shipment in shipments:
        original_invoice_parts = shipment.invoice_number.split('/')
        if len(original_invoice_parts) >= 6:
            return_types.add(original_invoice_parts[5])  # Should be RET or NONRET
    
    # If all shipments have the same return type, use it; otherwise use RET as default
    if len(return_types) == 1:
        return_type = return_types.pop()
    else:
        return_type = 'RET'  # Default when mixed types
    
    unique_ids_str = '/'.join(unique_ids)
    
    combined_invoice = f"NCPOR/ARC/{year}/{month}/EXP/{return_type}/{unique_ids_str}/{next_serial}"
    
    print(f"📦 Combined Shipment Details:")
    print(f"   Invoice Number: {combined_invoice}")
    print(f"   Total Packages: {total_packages}")
    print(f"   Unique IDs: {unique_ids_str}")
    print(f"   Serial Number: {next_serial}")
    print(f"   Return Type: {return_type}")
    print()
    
    print(f"📋 Individual Shipments Being Combined:")
    for i, shipment in enumerate(shipments, 1):
        user = shipment.created_by_user
        print(f"   {i}. {shipment.invoice_number}")
        print(f"      User: {user.first_name} {user.last_name} ({user.unique_id})")
        print(f"      Packages: {shipment.total_packages}")
    print()
    
    if total_packages > 20:
        print("⚠️  WARNING: Combined shipment would exceed 20 package limit!")
        print(f"   Total packages: {total_packages} > 20")
    else:
        print(f"✅ Package count OK: {total_packages} ≤ 20")
    
    print(f"\n🔗 Test URLs (after running Flask app):")
    print(f"   Admin Dashboard: http://localhost:5000/dashboard")
    print(f"   Direct Combine Form: http://localhost:5000/admin/combine")
    
    return combined_invoice, total_packages

def main():
    """Main function"""
    app = create_app()
    
    with app.app_context():
        print("🧪 COMPASS Combined Shipment Debug Tool")
        print("=" * 60)
        
        # List available shipments
        shipments = list_test_shipments()
        
        if not shipments:
            return
        
        # Show what combining all would look like
        print("\n🔄 Simulation: Combining ALL test shipments")
        print("=" * 60)
        
        all_ids = [s.id for s in shipments]
        simulate_combine_process(all_ids)
        
        print("\n" + "=" * 60)
        print("🧪 How to test manually:")
        print("1. Start the Flask app: python app.py")
        print("2. Login as admin")
        print("3. Go to Admin Dashboard")
        print("4. Click the red 'DEBUG: Test Combine Form' button")
        print("5. Or select shipments and use 'Combine Selected'")
        print("\n📊 Current Database State:")
        print(f"   Total Users: {User.query.count()}")
        print(f"   Total Shipments: {Shipment.query.count()}")
        print(f"   Export Shipments: {Shipment.query.filter_by(shipment_type='export').count()}")
        print(f"   Combined Shipments: {Shipment.query.filter_by(is_combined=True).count()}")

if __name__ == '__main__':
    main() 