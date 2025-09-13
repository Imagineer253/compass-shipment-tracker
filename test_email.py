#!/usr/bin/env python3
"""
Test script to verify email configuration for COMPASS
Run this after setting up the MAIL_PASSWORD environment variable
"""

import os
import sys
from compass import create_app
from compass.email_service import send_otp_email

def test_email_config():
    """Test email configuration"""
    print("🧪 Testing COMPASS Email Configuration...")
    print("="*50)
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        # Check configuration
        print(f"📧 MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"📧 MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"📧 MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
        print(f"📧 MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"📧 MAIL_PASSWORD configured: {bool(app.config.get('MAIL_PASSWORD'))}")
        print(f"📧 MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        
        # Check if password is set
        if not app.config.get('MAIL_PASSWORD'):
            print("\n❌ ERROR: MAIL_PASSWORD is not configured!")
            print("📋 Please follow these steps:")
            print("1. Set up Gmail App Password for arctic.ncpor@gmail.com")
            print("2. Set environment variable: MAIL_PASSWORD=your-app-password")
            print("3. Restart this script")
            return False
        
        print(f"\n📧 Password configured: {'✅ Yes' if app.config.get('MAIL_PASSWORD') else '❌ No'}")
        
        # Test email sending
        test_email = input("\n📧 Enter test email address (or press Enter to skip): ").strip()
        
        if test_email:
            print(f"\n📤 Sending test email to {test_email}...")
            
            # Generate test OTP
            test_otp = "123456"
            
            try:
                success = send_otp_email(
                    email=test_email,
                    name="Test User",
                    otp_code=test_otp,
                    purpose='registration'
                )
                
                if success:
                    print("✅ Test email sent successfully!")
                    print(f"📧 Check {test_email} for the verification email")
                    print(f"🔢 Test OTP code: {test_otp}")
                else:
                    print("❌ Failed to send test email")
                    print("🔍 Check the application logs for error details")
                    
            except Exception as e:
                print(f"❌ Email test failed: {str(e)}")
                return False
        
        print("\n✅ Email configuration test completed!")
        return True

def test_smtp_connection():
    """Test direct SMTP connection"""
    print("\n🔌 Testing direct SMTP connection...")
    
    try:
        import smtplib
        
        # Get credentials
        username = "arctic.ncpor@gmail.com"
        password = os.environ.get('MAIL_PASSWORD')
        
        if not password:
            print("❌ MAIL_PASSWORD environment variable not set")
            return False
        
        # Test connection
        print("🔗 Connecting to smtp.gmail.com:587...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        
        print("🔒 Starting TLS...")
        server.starttls()
        
        print("🔑 Authenticating...")
        server.login(username, password)
        
        print("✅ SMTP connection successful!")
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ SMTP connection failed: {str(e)}")
        print("\n🔍 Common issues:")
        print("- App Password not generated or incorrect")
        print("- 2FA not enabled on Gmail account") 
        print("- Network connectivity issues")
        return False

if __name__ == "__main__":
    print("🧭 COMPASS Email Configuration Test")
    print("="*40)
    
    # Test SMTP first
    smtp_ok = test_smtp_connection()
    
    if smtp_ok:
        # Test Flask-Mail integration
        app_ok = test_email_config()
        
        if app_ok:
            print("\n🎉 All email tests passed!")
            print("✅ Email verification should work during signup")
        else:
            print("\n⚠️  SMTP works but Flask-Mail has issues")
    else:
        print("\n❌ SMTP connection failed - fix this first")
        print("📋 See email_setup_instructions.md for help")
    
    print("\n" + "="*40)
    print("📚 For detailed setup instructions, see: email_setup_instructions.md")
