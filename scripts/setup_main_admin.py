#!/usr/bin/env python3
"""
Script to set up the main admin user for COMPASS
"""

import sys
import os

# Add the compass directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'compass'))

from compass import create_app
from compass.models import User, Role, db
from werkzeug.security import generate_password_hash

def setup_main_admin():
    """Set up the main admin user"""
    
    app = create_app()
    with app.app_context():
        print("Setting up main admin user...")
        
        # Initialize roles if they don't exist
        roles = ['Admin', 'Project Incharge', 'Field Personnel']
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(
                    name=role_name,
                    description=f'{role_name} role for COMPASS system'
                )
                db.session.add(role)
        
        db.session.commit()
        
        # Get admin role
        admin_role = Role.query.filter_by(name='Admin').first()
        
        # Check if admin user exists
        admin_email = 'sarabagnus@gmail.com'
        admin_password = 'arctic@123'
        
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if existing_admin:
            print(f"Admin user {admin_email} already exists. Updating password and ensuring admin role...")
            
            # Update password
            existing_admin.password = generate_password_hash(admin_password)
            
            # Clear all existing roles first
            existing_admin.roles.clear()
            
            # Ensure ONLY admin role is assigned
            existing_admin.roles.append(admin_role)
            
            print(f"Updated admin user: {admin_email} (Admin role only)")
        else:
            print(f"Creating new admin user: {admin_email}")
            
            # Create new admin user
            admin_user = User(
                email=admin_email,
                password=generate_password_hash(admin_password),
                first_name='Sara',
                last_name='Bagnus',
                phone='+1234567890',
                organization='NCPOR',
                is_active=True
            )
            
            # Assign ONLY admin role
            admin_user.roles.append(admin_role)
            
            db.session.add(admin_user)
            print(f"Created new admin user: {admin_email} (Admin role only)")
        
        try:
            db.session.commit()
            print("\n✅ Main admin setup completed successfully!")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
            print(f"   Role: Admin")
        except Exception as e:
            print(f"\n❌ Error setting up admin: {e}")
            db.session.rollback()

if __name__ == "__main__":
    setup_main_admin() 