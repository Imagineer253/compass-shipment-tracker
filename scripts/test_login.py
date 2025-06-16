#!/usr/bin/env python3
"""
Test script to debug login issues
"""
from compass import create_app
from compass.models import User
from werkzeug.security import check_password_hash

def test_login():
    app = create_app()
    
    with app.app_context():
        # Get all users
        users = User.query.all()
        print(f"Total users in database: {len(users)}")
        
        if not users:
            print("❌ No users found in database!")
            return
        
        for user in users:
            print(f"\n👤 User: {user.email}")
            print(f"   Active: {user.is_active}")
            print(f"   Roles: {[role.name for role in user.roles]}")
            
            # Test with common passwords
            test_passwords = ['admin', 'password', '123456', 'admin123', 'test123']
            
            for test_pwd in test_passwords:
                if check_password_hash(user.password, test_pwd):
                    print(f"   ✅ Password '{test_pwd}' works!")
                    return user.email, test_pwd
        
        print("\n❌ No working passwords found with common tests")
        print("\nTrying to create a test admin user...")
        
        # Create a test admin user
        from compass.models import Role, db
        from werkzeug.security import generate_password_hash
        
        # Check if admin role exists
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            admin_role = Role(name='Admin', description='Administrator')
            db.session.add(admin_role)
        
        # Create test admin
        test_email = "admin@test.com"
        test_password = "admin123"
        
        existing_user = User.query.filter_by(email=test_email).first()
        if existing_user:
            print(f"Test user {test_email} already exists")
        else:
            test_user = User(
                email=test_email,
                password=generate_password_hash(test_password),
                first_name="Test",
                last_name="Admin",
                phone="1234567890",
                organization="Test Org",
                is_active=True
            )
            test_user.roles.append(admin_role)
            db.session.add(test_user)
            db.session.commit()
            print(f"✅ Created test admin: {test_email} / {test_password}")
        
        return test_email, test_password

if __name__ == "__main__":
    credentials = test_login()
    if credentials:
        email, password = credentials
        print(f"\n🎉 Login credentials: {email} / {password}")
    else:
        print("\n❌ Could not determine working credentials") 