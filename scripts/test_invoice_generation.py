#!/usr/bin/env python3
"""
Test script to debug invoice generation for combined shipments
Run this from the project root directory: python scripts/test_invoice_generation.py
"""

import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compass import create_app, db
from compass.models import User, Shipment, ShipmentSerialCounter

def test_invoice_generation():
    """Test the invoice generation logic directly"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing Invoice Generation Logic")
        print("=" * 50)
        
        # Get test shipments
        shipments = Shipment.query.filter_by(
            shipment_type='export',
            status='Submitted'
        ).filter(
            Shipment.is_combined == False
        ).limit(3).all()
        
        if not shipments:
            print("❌ No test shipments found!")
            print("Run 'python scripts/create_test_combined_exports.py' first")
            return
        
        print(f"📋 Found {len(shipments)} test shipments:")
        for i, shipment in enumerate(shipments, 1):
            user = shipment.created_by_user
            print(f"  {i}. {shipment.invoice_number}")
            print(f"     User: {user.first_name} {user.last_name} (ID: {user.id})")
            print(f"     Unique ID: {user.unique_id}")
            print(f"     Created by: {shipment.created_by}")
            print()
        
        # Test the invoice generation logic
        print("🔄 Testing Invoice Generation...")
        print("-" * 30)
        
        # Simulate the logic from admin_combine_form
        first_shipment = shipments[0]
        
        print(f"DEBUG: Starting invoice generation for {len(shipments)} shipments")
        print(f"DEBUG: First shipment type: {first_shipment.shipment_type}")
        
        # Get current date for proper format
        from datetime import datetime
        current_date = datetime.now()
        year = current_date.strftime('%Y')
        month = current_date.strftime('%b').upper()  # JAN, FEB, MAR, etc.
        
        print(f"DEBUG: Date components - Year: {year}, Month: {month}")
        
        # Get next serial number for the combined shipment
        try:
            serial_number = ShipmentSerialCounter.get_next_serial()
            print(f"DEBUG: Generated serial number: {serial_number}")
        except Exception as e:
            print(f"DEBUG: Error getting serial number: {e}")
            serial_number = "0001"  # Fallback
        
        # Collect unique IDs from all shipments being combined
        unique_user_ids = []
        seen_users = set()
        
        print(f"DEBUG: Collecting unique user IDs...")
        for i, shipment in enumerate(shipments):
            print(f"DEBUG: Processing shipment {i+1}: {shipment.invoice_number}")
            user_id = shipment.created_by
            print(f"DEBUG: Shipment {i+1} created_by: {user_id}")
            
            if user_id not in seen_users:
                try:
                    user = User.query.get(user_id)
                    if user:
                        print(f"DEBUG: Found user: {user.first_name} {user.last_name}, unique_id: {user.unique_id}")
                        if user.unique_id:
                            unique_user_ids.append(user.unique_id)
                            seen_users.add(user_id)
                        else:
                            print(f"DEBUG: WARNING - User {user.first_name} {user.last_name} has no unique_id!")
                    else:
                        print(f"DEBUG: WARNING - User with ID {user_id} not found!")
                except Exception as e:
                    print(f"DEBUG: Error getting user {user_id}: {e}")
        
        # Ensure we have at least one unique ID
        if not unique_user_ids:
            print(f"DEBUG: WARNING - No unique IDs found, using fallback")
            unique_user_ids = ["UNKNOWN"]
        
        # Create combined unique IDs string
        unique_ids_str = "/".join(unique_user_ids)
        print(f"DEBUG: Combined unique IDs: {unique_ids_str}")
        
        # Generate invoice number following the correct format
        try:
            if first_shipment.shipment_type == 'export':
                # Extract return type from ALL shipments being combined to determine the type
                return_types = set()
                print(f"DEBUG: Analyzing return types from all shipments...")
                
                for shipment in shipments:
                    print(f"DEBUG: Analyzing invoice: {shipment.invoice_number}")
                    original_invoice_parts = shipment.invoice_number.split('/')
                    print(f"DEBUG: Invoice parts: {original_invoice_parts}")
                    
                    if len(original_invoice_parts) >= 6:
                        return_type_part = original_invoice_parts[5]
                        return_types.add(return_type_part)
                        print(f"DEBUG: Found return type: {return_type_part}")
                    else:
                        print(f"DEBUG: Invoice format doesn't have return type at position 5")
                
                # If all shipments have the same return type, use it; otherwise use RET as default
                if len(return_types) == 1:
                    return_type = return_types.pop()
                    print(f"DEBUG: All shipments have same return type: {return_type}")
                else:
                    return_type = 'RET'  # Default when mixed types
                    print(f"DEBUG: Mixed or no return types found, using default: {return_type}")
                
                combined_invoice = f"NCPOR/ARC/{year}/{month}/EXP/{return_type}/{unique_ids_str}/{serial_number}"
                
            elif first_shipment.shipment_type == 'import':
                combined_invoice = f"NCPOR/IMP/{year}/{month}/RESEARCH/{unique_ids_str}/{serial_number}"
                
            elif first_shipment.shipment_type == 'reimport':
                combined_invoice = f"NCPOR/REIMP/{year}/{month}/RESEARCH/{unique_ids_str}/{serial_number}"
                
            else:  # cold
                combined_invoice = f"NCPOR/COLD/{year}/{month}/{unique_ids_str}/{serial_number}"
            
            print(f"DEBUG: Successfully generated combined invoice: {combined_invoice}")
            
        except Exception as e:
            print(f"DEBUG: Error in invoice format generation: {e}")
            import traceback
            traceback.print_exc()
            combined_invoice = f"COMBINED/ERROR"
            print(f"DEBUG: Using error fallback format: {combined_invoice}")
        
        print("\n" + "=" * 50)
        print("✅ Test Results:")
        print(f"📊 Processed {len(shipments)} shipments")
        print(f"👥 Found {len(unique_user_ids)} unique users")
        print(f"🎯 Generated Invoice: {combined_invoice}")
        print(f"📅 Date Format: {year}/{month}")
        print(f"🔢 Serial Number: {serial_number}")
        print(f"🏷️  Unique IDs: {unique_ids_str}")
        
        # Expected vs Actual
        expected_format = f"NCPOR/ARC/{year}/{month}/EXP/RET/{unique_ids_str}/{serial_number}"
        print(f"\n📋 Expected Format: {expected_format}")
        print(f"🎯 Actual Result:   {combined_invoice}")
        
        if combined_invoice == expected_format:
            print("✅ SUCCESS: Invoice format matches expected!")
        else:
            print("❌ MISMATCH: Invoice format doesn't match expected!")

if __name__ == '__main__':
    test_invoice_generation() 