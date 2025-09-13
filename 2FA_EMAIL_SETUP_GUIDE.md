# Two-Factor Authentication & Email Verification Setup Guide

## Overview
This guide explains the newly implemented two-factor authentication (2FA) and email verification features in the COMPASS shipment management system.

## New Features

### 🔐 **Two-Factor Authentication (2FA)**
- **Optional** for all users - users can enable/disable as needed
- **TOTP-based** using authenticator apps (Google Authenticator, Authy, Microsoft Authenticator)
- **Backup codes** for emergency access
- **Email-based 2FA** as an alternative verification method
- **QR code setup** for easy authenticator app configuration

### 📧 **Email Verification**
- **Required** for all new user registrations
- **OTP-based** verification with 6-digit codes
- **15-minute expiration** for security
- **Automated emails** sent from arctic.ncpor@gmail.com
- **Professional templates** with Arctic theme

## Setup Instructions

### 1. Gmail SMTP Configuration

To enable email functionality, you need to configure Gmail SMTP:

1. **Enable 2FA on arctic.ncpor@gmail.com**:
   - Go to Google Account settings
   - Enable 2-factor authentication

2. **Generate App Password**:
   - Go to Google Account > Security > App passwords
   - Generate a new app password for "COMPASS"
   - Use this password in the environment configuration

3. **Create Environment File**:
   ```bash
   # Copy env_example.txt to .env
   cp env_example.txt .env
   
   # Edit .env with your actual values
   MAIL_PASSWORD=your-generated-app-password
   ```

### 2. Install Required Dependencies

The new features require additional Python packages:

```bash
pip install pyotp==2.9.0 qrcode==7.4.2 Pillow==10.2.0
```

Or simply install from requirements.txt:
```bash
pip install -r requirements.txt
```

### 3. Database Migration

Apply the database migration to add 2FA fields:

```bash
python -m flask --app app.py db upgrade
```

## User Workflows

### New User Registration Flow

1. **User fills registration form** → System validates input
2. **OTP sent to email** → User receives 6-digit verification code
3. **User enters OTP** → System verifies code and creates account
4. **Account activated** → User can log in normally

### Login Flow (with 2FA enabled)

1. **User enters email/password** → System validates credentials
2. **2FA verification required** → Multiple options available:
   - **Authenticator app code** (primary method)
   - **Email OTP** (backup method)
   - **Backup codes** (emergency access)
3. **Successful verification** → User logged in

### 2FA Setup Flow

1. **User visits Security Settings** → Access via profile page
2. **Setup authenticator app** → Scan QR code or enter secret manually
3. **Verify setup** → Enter code from authenticator app
4. **Backup codes generated** → User must save these securely
5. **2FA enabled** → Required for all future logins

## File Structure

### New Files Added:
```
compass/
├── email_service.py          # Email templates and sending functions
├── two_fa.py                 # 2FA routes and management
└── templates/auth/
    ├── 2fa_setup.html        # 2FA setup page with QR code
    ├── 2fa_verify.html       # 2FA verification during login
    ├── 2fa_manage.html       # 2FA management dashboard
    ├── 2fa_backup_codes.html # Backup codes display
    └── verify_otp.html       # Email verification page (updated)
```

### Modified Files:
```
compass/
├── models.py                 # Added 2FA and email verification fields
├── auth.py                   # Updated signup/login flows
├── config.py                # Added SMTP and 2FA configuration
├── __init__.py              # Registered 2FA blueprint
└── templates/auth/
    └── profile.html         # Added security section with 2FA management
```

## Database Schema Changes

### User Model - New Fields:
- `email_verified` (Boolean) - Email verification status
- `email_verification_token` (String) - Temporary verification token
- `email_verification_expires` (DateTime) - Token expiration time
- `two_fa_enabled` (Boolean) - 2FA status
- `two_fa_secret` (String) - TOTP secret key
- `backup_codes` (Text) - JSON array of backup codes

### New EmailOTP Model:
- Stores temporary OTP codes for email verification
- Supports multiple purposes (registration, login, password reset)
- Automatic expiration and attempt limiting

## Security Features

### Email Verification Security:
- ✅ **6-digit OTP codes** - Secure but user-friendly
- ✅ **15-minute expiration** - Prevents code reuse
- ✅ **Attempt limiting** - Max 5 attempts per OTP
- ✅ **Automatic invalidation** - Old codes cancelled when new ones generated

### 2FA Security:
- ✅ **TOTP standard** - Compatible with all major authenticator apps
- ✅ **30-second time windows** - Standard TOTP timing
- ✅ **Backup codes** - 10 single-use emergency codes
- ✅ **Secure secret generation** - Cryptographically secure random keys

## User Interface Features

### Professional Email Templates:
- **Arctic-themed design** matching COMPASS branding
- **Mobile-responsive** HTML templates
- **Clear instructions** and security information
- **Professional formatting** suitable for NCPOR

### Modern Web Interface:
- **Bootstrap-based** responsive design
- **Font Awesome icons** for better UX
- **Interactive elements** (QR codes, copy buttons, etc.)
- **Progressive enhancement** with JavaScript features

## API Endpoints

### 2FA Management:
- `GET /2fa/setup` - 2FA setup page with QR code
- `POST /2fa/enable` - Enable 2FA after verification
- `POST /2fa/disable` - Disable 2FA with password confirmation
- `GET /2fa/manage` - 2FA management dashboard
- `GET /2fa/backup-codes` - Generate new backup codes

### 2FA Verification:
- `GET/POST /2fa/verify` - Main 2FA verification page
- `POST /2fa/verify-email` - Send OTP via email
- `POST /2fa/verify-email-code` - Verify email OTP

### Email Verification:
- `GET/POST /auth/verify-email` - Email verification page
- `POST /auth/resend-verification` - Resend verification email

## Configuration Options

### Environment Variables:
```bash
# Email Settings
MAIL_USERNAME=arctic.ncpor@gmail.com
MAIL_PASSWORD=app-password-here
MAIL_DEFAULT_SENDER=arctic.ncpor@gmail.com

# 2FA Settings
TWO_FA_APP_NAME=COMPASS-NCPOR
OTP_EXPIRY_MINUTES=15
```

### Application Settings:
- **OTP expiry time** - Configurable (default 15 minutes)
- **App name for 2FA** - Appears in authenticator apps
- **Backup code count** - Default 10 codes
- **Email templates** - Customizable HTML templates

## Testing & Validation

### Pre-deployment Checklist:
- [ ] Gmail SMTP configuration working
- [ ] Database migration applied successfully
- [ ] Email templates rendering correctly
- [ ] QR codes generating properly
- [ ] 2FA verification working with authenticator apps
- [ ] Backup codes functional
- [ ] Email verification working for new registrations

### Test User Flows:
1. **New registration** with email verification
2. **2FA setup** and verification
3. **Login with 2FA** using different methods
4. **Backup code usage** and regeneration
5. **2FA disable/re-enable** process

## Security Recommendations

### For Administrators:
1. **Monitor failed 2FA attempts** - Set up logging/alerts
2. **Regular backup code audits** - Ensure users have saved codes
3. **Email deliverability** - Monitor email sending success rates
4. **SMTP security** - Use app passwords, not account passwords

### For Users:
1. **Save backup codes securely** - Use password managers or physical storage
2. **Keep authenticator app updated** - Ensure app compatibility
3. **Verify email access** - Ensure email account is secure
4. **Regular security reviews** - Periodically check 2FA status

## Troubleshooting

### Common Issues:

**Email not sending:**
- Check Gmail app password configuration
- Verify SMTP settings in .env file
- Check Gmail account 2FA is enabled

**QR code not displaying:**
- Ensure Pillow library is installed correctly
- Check file permissions for temporary files
- Verify qrcode package installation

**2FA codes not working:**
- Check device time synchronization
- Verify app is TOTP-compatible
- Try backup codes if available

**Database errors:**
- Run migration: `flask db upgrade`
- Check database file permissions
- Verify SQLite installation

## Support

For technical support or questions about the 2FA implementation:
1. Check the application logs for error details
2. Verify environment configuration
3. Test email sending functionality separately
4. Contact NCPOR IT support if issues persist

---

**Implementation Status**: ✅ **COMPLETE**
**Security Level**: 🔒 **HIGH**
**User Experience**: 👍 **ENHANCED**
