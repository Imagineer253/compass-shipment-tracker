#!/usr/bin/env python3
"""
Script to create test export shipments for testing combined shipment functionality
Run this from the project root directory: python scripts/create_test_combined_exports.py
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compass import create_app, db
from compass.models import User, Shipment, ShipmentSerialCounter
from werkzeug.security import generate_password_hash

def create_test_users():
    """Create test users if they don't exist"""
    test_users = [
        {
            'email': 'researcher1@ncpor.gov.in',
            'password': 'test123',
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'phone': '+91 9876543210',
            'organization': 'NCPOR',
            'unique_id': 'AL1CE1'
        },
        {
            'email': 'researcher2@ncpor.gov.in',
            'password': 'test123',
            'first_name': 'Bob',
            'last_name': 'Smith',
            'phone': '+91 9876543211',
            'organization': 'NCPOR',
            'unique_id': 'BOB2SM'
        },
        {
            'email': 'researcher3@ncpor.gov.in',
            'password': 'test123',
            'first_name': 'Carol',
            'last_name': 'Davis',
            'phone': '+91 9876543212',
            'organization': 'NCPOR',
            'unique_id': 'CAR0LD'
        }
    ]
    
    created_users = []
    for user_data in test_users:
        # Check if user already exists
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if existing_user:
            print(f"User {user_data['email']} already exists, using existing user")
            created_users.append(existing_user)
            continue
            
        # Create new user
        user = User(
            email=user_data['email'],
            password=generate_password_hash(user_data['password']),
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone=user_data['phone'],
            organization=user_data['organization'],
            unique_id=user_data['unique_id']
        )
        
        db.session.add(user)
        created_users.append(user)
        print(f"Created user: {user_data['first_name']} {user_data['last_name']} ({user_data['unique_id']})")
    
    db.session.commit()
    return created_users

def create_test_export_shipments(users):
    """Create test export shipments for combining"""
    
    # Get current date info
    current_date = datetime.now()
    year = current_date.strftime('%Y')
    month = current_date.strftime('%b').upper()
    
    test_shipments = []
    
    for i, user in enumerate(users):
        # Get next serial number
        serial_number = ShipmentSerialCounter.get_next_serial()
        
        # Create invoice number
        invoice_number = f"NCPOR/ARC/{year}/{month}/EXP/RET/{user.unique_id}/{serial_number}"
        
        # Create form data for the shipment
        form_data = {
            'shipment_type': 'export',
            'requester_name': f"{user.first_name} {user.last_name}",
            'expedition_year': year,
            'batch_number': f'BATCH{i+1:02d}',
            'return_type': 'RET',
            'destination_country': 'NORWAY',
            'final_destination': 'Ny-Ålesund',
            'mode_of_transport': 'Air',
            'port_of_discharge': 'Oslo Airport',
            'exporter': 'ncpor',
            'consignee': 'himadri',
            'total_packages': 2,
            
            # Package 1
            'package_1_type': 'cardboard_box',
            'package_1_length': '50',
            'package_1_width': '40',
            'package_1_height': '30',
            'package_1_items_count': '2',
            'package_1_item_1_description': f'Research Equipment Set A - {user.first_name}',
            'package_1_item_1_hsn_code': '9015.80.90',
            'package_1_item_1_quantity': '1',
            'package_1_item_1_unit_value': '500.00',
            'package_1_item_1_net_weight': '5.0',
            'package_1_item_1_attn': f"{user.first_name} {user.last_name}",
            'package_1_item_2_description': f'Scientific Instruments - {user.first_name}',
            'package_1_item_2_hsn_code': '9027.80.90',
            'package_1_item_2_quantity': '3',
            'package_1_item_2_unit_value': '200.00',
            'package_1_item_2_net_weight': '2.5',
            'package_1_item_2_attn': f"{user.first_name} {user.last_name}",
            
            # Package 2
            'package_2_type': 'plastic_crate',
            'package_2_length': '60',
            'package_2_width': '45',
            'package_2_height': '35',
            'package_2_items_count': '1',
            'package_2_item_1_description': f'Field Research Tools - {user.first_name}',
            'package_2_item_1_hsn_code': '8205.70.00',
            'package_2_item_1_quantity': '1',
            'package_2_item_1_unit_value': '800.00',
            'package_2_item_1_net_weight': '8.0',
            'package_2_item_1_attn': f"{user.first_name} {user.last_name}",
        }
        
        # Create shipment
        shipment = Shipment(
            invoice_number=invoice_number,
            serial_number=serial_number,
            shipment_type='export',
            status='Submitted',
            created_by=user.id,
            requester_name=form_data['requester_name'],
            expedition_year=form_data['expedition_year'],
            batch_number=form_data['batch_number'],
            destination_country=form_data['destination_country'],
            total_packages=int(form_data['total_packages']),
            form_data=json.dumps(form_data)
        )
        
        db.session.add(shipment)
        test_shipments.append(shipment)
        print(f"Created test shipment: {invoice_number}")
    
    db.session.commit()
    return test_shipments

def main():
    """Main function to create test data"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Creating test data for combined exports...")
        print("=" * 50)
        
        # Create test users
        print("\n1. Creating test users...")
        users = create_test_users()
        
        # Create test shipments
        print("\n2. Creating test export shipments...")
        shipments = create_test_export_shipments(users)
        
        print("\n" + "=" * 50)
        print("✅ Test data created successfully!")
        print(f"📊 Created {len(users)} test users")
        print(f"📦 Created {len(shipments)} test export shipments")
        print("\n🔗 Test users created:")
        for user in users:
            print(f"   • {user.first_name} {user.last_name} ({user.unique_id}) - {user.email}")
        
        print("\n📋 Test shipments created:")
        for shipment in shipments:
            print(f"   • {shipment.invoice_number} - {shipment.requester_name}")
        
        print("\n🧪 How to test:")
        print("1. Go to Admin Dashboard")
        print("2. Click the red 'DEBUG: Test Combine Form' button")
        print("3. Or select the test shipments and use 'Combine Selected'")
        print("4. Test the combined export with up to 20 packages")
        
        print("\n⚠️  Remember to remove the debug button later!")

if __name__ == '__main__':
    main() 