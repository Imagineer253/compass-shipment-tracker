#!/usr/bin/env python3
"""
Setup admin user and roles for COMPASS system
"""
from compass import create_app
from compass.models import User, Role, db
from werkzeug.security import generate_password_hash

def setup_admin():
    app = create_app()
    
    with app.app_context():
        print("🔧 Setting up COMPASS admin user and roles...")
        
        # Create roles if they don't exist
        roles_to_create = [
            ('Admin', 'System Administrator'),
            ('Project Incharge', 'Project Incharge - can create and edit shipments'),
            ('Field Personnel', 'Field Personnel - can create and edit shipments'),
            ('Viewer', 'View-only access')
        ]
        
        for role_name, description in roles_to_create:
            existing_role = Role.query.filter_by(name=role_name).first()
            if not existing_role:
                role = Role(name=role_name, description=description)
                db.session.add(role)
                print(f"✅ Created role: {role_name}")
            else:
                print(f"ℹ️  Role already exists: {role_name}")
        
        db.session.commit()
        
        # Create admin user
        admin_email = "admin@compass.com"
        admin_password = "admin123"
        
        existing_admin = User.query.filter_by(email=admin_email).first()
        if existing_admin:
            print(f"ℹ️  Admin user already exists: {admin_email}")
            # Make sure the user is active and has admin role
            existing_admin.is_active = True
            admin_role = Role.query.filter_by(name='Admin').first()
            if admin_role not in existing_admin.roles:
                existing_admin.roles.append(admin_role)
            db.session.commit()
        else:
            admin_role = Role.query.filter_by(name='Admin').first()
            admin_user = User(
                email=admin_email,
                password=generate_password_hash(admin_password),
                first_name="System",
                last_name="Administrator",
                phone="1234567890",
                organization="NCPOR",
                is_active=True
            )
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
            db.session.commit()
            print(f"✅ Created admin user: {admin_email}")
        
        # Create a test PI user
        pi_email = "pi@compass.com"
        pi_password = "pi123"
        
        existing_pi = User.query.filter_by(email=pi_email).first()
        if not existing_pi:
            pi_role = Role.query.filter_by(name='Project Incharge').first()
            pi_user = User(
                email=pi_email,
                password=generate_password_hash(pi_password),
                first_name="Test",
                last_name="PI",
                phone="9876543210",
                organization="Research Institute",
                is_active=True
            )
            pi_user.roles.append(pi_role)
            db.session.add(pi_user)
            db.session.commit()
            print(f"✅ Created PI user: {pi_email}")
        
        # Create a test Field Personnel user
        field_email = "field@compass.com"
        field_password = "field123"
        
        existing_field = User.query.filter_by(email=field_email).first()
        if not existing_field:
            field_role = Role.query.filter_by(name='Field Personnel').first()
            field_user = User(
                email=field_email,
                password=generate_password_hash(field_password),
                first_name="Test",
                last_name="Field",
                phone="5555555555",
                organization="Field Operations",
                is_active=True
            )
            field_user.roles.append(field_role)
            db.session.add(field_user)
            db.session.commit()
            print(f"✅ Created Field Personnel user: {field_email}")
        
        print("\n🎉 Setup complete! Login credentials:")
        print(f"   👨‍💼 Admin: {admin_email} / {admin_password}")
        print(f"   👨‍🔬 PI: {pi_email} / {pi_password}")
        print(f"   👨‍🔧 Field: {field_email} / {field_password}")
        
        print(f"\n📊 Total users in database: {User.query.count()}")
        print(f"📊 Total roles in database: {Role.query.count()}")

if __name__ == "__main__":
    setup_admin() 