#!/usr/bin/env python3
"""
Setup script to create default signing authorities for COMPASS system.
Run this script after database migration to add the default signing authorities.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compass import create_app, db
from compass.models import SigningAuthority, User, Role

def setup_default_signing_authorities():
    """Create default signing authorities"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if there's an admin user to assign as creator
            admin_user = User.query.join(User.roles).filter(Role.name == 'Admin').first()
            if not admin_user:
                print("❌ No admin user found. Please create an admin user first.")
                return False
            
            # Check if signing authorities already exist
            existing_authorities = SigningAuthority.query.count()
            if existing_authorities > 0:
                print(f"ℹ️ {existing_authorities} signing authorities already exist in the database.")
                return True
            
            # Default signing authorities
            default_authorities = [
                {
                    'name': 'Dr. M. Ravichandran',
                    'designation': 'Director',
                    'department': 'National Center for Polar and Ocean Research',
                    'organisation': 'Ministry of Earth Sciences, Government of India',
                    'contact_number': '+91 832 2525501',
                    'contact_fax': '+91 832 2520877',
                    'email': 'director@ncpor.res.in',
                    'is_default': True,
                    'is_active': True
                },
                {
                    'name': 'Dr. Shridhar D. Jawak',
                    'designation': 'Scientist',
                    'department': 'Polar Remote Sensing Division',
                    'organisation': 'National Center for Polar and Ocean Research',
                    'contact_number': '+91 832 2525501',
                    'contact_fax': '+91 832 2520877',
                    'email': 'shridhar@ncpor.res.in',
                    'is_default': False,
                    'is_active': True
                },
                {
                    'name': 'Dr. Rahul Mohan',
                    'designation': 'Group Director',
                    'department': 'Ocean Science Group',
                    'organisation': 'National Center for Polar and Ocean Research',
                    'contact_number': '+91 832 2525501',
                    'contact_fax': '+91 832 2520877',
                    'email': 'rahulm@ncpor.res.in',
                    'is_default': False,
                    'is_active': True
                }
            ]
            
            print("🔄 Creating default signing authorities...")
            
            for authority_data in default_authorities:
                authority = SigningAuthority(
                    name=authority_data['name'],
                    designation=authority_data['designation'],
                    department=authority_data['department'],
                    organisation=authority_data['organisation'],
                    contact_number=authority_data['contact_number'],
                    contact_fax=authority_data['contact_fax'],
                    email=authority_data['email'],
                    is_default=authority_data['is_default'],
                    is_active=authority_data['is_active'],
                    created_by=admin_user.id
                )
                db.session.add(authority)
                print(f"  ✅ Added: {authority_data['name']} - {authority_data['designation']}")
            
            db.session.commit()
            print(f"\n🎉 Successfully created {len(default_authorities)} default signing authorities!")
            print("\n📋 Summary:")
            for i, authority_data in enumerate(default_authorities, 1):
                default_mark = " (DEFAULT)" if authority_data['is_default'] else ""
                print(f"  {i}. {authority_data['name']} - {authority_data['designation']}{default_mark}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating signing authorities: {str(e)}")
            db.session.rollback()
            return False

def main():
    """Main function"""
    print("🚀 COMPASS Signing Authorities Setup")
    print("=" * 50)
    
    success = setup_default_signing_authorities()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Start your COMPASS application")
        print("2. Login as admin")
        print("3. Go to 'Signing Authorities' in the navigation")
        print("4. Review and edit the signing authorities as needed")
        print("5. The default authority will be automatically used for document generation")
    else:
        print("\n❌ Setup failed. Please check the errors above and try again.")
        sys.exit(1)

if __name__ == '__main__':
    main() 