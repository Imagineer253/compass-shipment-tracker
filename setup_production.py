#!/usr/bin/env python3
"""
Production setup script for COMPASS
Run this once on your server laptop
"""
import os
import sys
from dotenv import load_dotenv
from compass import create_app
from compass.models import db, User, Role
from flask_migrate import upgrade
import secrets

def setup_production():
    """Set up production environment"""
    
    print("🧭 COMPASS Production Setup")
    print("=" * 50)
    
    # Load environment
    if os.path.exists('production.env'):
        load_dotenv('production.env')
    else:
        load_dotenv()
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        # Create instance directory
        instance_dir = os.path.join(app.root_path, '..', 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        
        # Create upload directories
        upload_dirs = [
            'compass/static/uploads/profile_pictures',
            'compass/static/uploads/passports',
            'compass/static/qrcodes'
        ]
        
        for dir_path in upload_dirs:
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ Created directory: {dir_path}")
        
        try:
            # Run database migrations
            print("🗄️  Setting up database...")
            upgrade()
            print("✅ Database migrations completed")
            
            # Create admin user if not exists
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@compass.com')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            
            existing_admin = User.query.filter_by(email=admin_email).first()
            if not existing_admin:
                admin_user = User(
                    email=admin_email,
                    first_name='Admin',
                    last_name='User',
                    role='admin',
                    is_verified=True,
                    is_email_verified=True
                )
                admin_user.set_password(admin_password)
                db.session.add(admin_user)
                db.session.commit()
                print(f"✅ Created admin user: {admin_email}")
            else:
                print(f"ℹ️  Admin user already exists: {admin_email}")
            
            # Generate secret key if not provided
            secret_key = os.environ.get('SECRET_KEY')
            if not secret_key or secret_key == 'your-super-secret-production-key-here':
                new_secret = secrets.token_urlsafe(32)
                print(f"🔐 Generated new secret key: {new_secret}")
                print("⚠️  Update your production.env with this secret key!")
            
            print("\n🎉 Production setup completed successfully!")
            print("\nNext steps:")
            print("1. Update production.env with your actual values")
            print("2. Start the server: python start_server.py")
            print("3. Start ngrok: ngrok start compass")
            print("4. Update QR codes with new domain in admin panel")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            sys.exit(1)

if __name__ == '__main__':
    setup_production()
