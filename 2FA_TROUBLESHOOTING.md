# Two-Factor Authentication Troubleshooting Guide

## Common Issues and Solutions

### Issue: "No module named PIL" Error

**Problem**: When setting up 2FA, you get an error about missing PIL module.

**Solution**:
1. Install Pillow (Python Imaging Library):
   ```bash
   pip install Pillow
   ```

2. Reinstall qrcode with PIL support:
   ```bash
   pip install --upgrade qrcode[pil]==7.4.2
   ```

3. Verify installation:
   ```bash
   python -c "import PIL; import qrcode; print('All dependencies installed correctly')"
   ```

### Issue: QR Code Not Displaying

**Problem**: The QR code doesn't appear on the 2FA setup page.

**Solution**:
1. Check browser console for JavaScript errors
2. Ensure image data is being generated correctly
3. Verify Flask app has write permissions for temporary files
4. Check if base64 encoding is working:
   ```bash
   python -c "from compass.two_fa import *; print('QR generation test passed')"
   ```

### Issue: TOTP Codes Not Working

**Problem**: Authenticator app codes are rejected.

**Possible Causes**:
- **Time synchronization**: Ensure server and mobile device clocks are synchronized
- **Secret key mismatch**: Re-scan QR code or manually enter secret
- **Code reuse**: TOTP codes can only be used once
- **Time window**: Codes are valid for 30 seconds

**Solution**:
1. Check time synchronization on both server and device
2. Regenerate 2FA setup (disable and re-enable)
3. Try backup codes if available
4. Verify authenticator app supports TOTP standard

### Issue: Backup Codes Not Working

**Problem**: Backup codes are rejected during login.

**Solution**:
1. Ensure you're using unused backup codes
2. Check for typos (codes are case-sensitive)
3. Generate new backup codes from profile page
4. Verify backup codes are saved correctly in database

### Issue: Email 2FA Not Working

**Problem**: Email OTP codes not being sent or received.

**Solution**:
1. Verify SMTP configuration:
   ```bash
   # Check .env file
   MAIL_USERNAME=arctic.ncpor@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

2. Test email sending:
   ```bash
   python -c "from compass.email_service import send_otp_email; print('Email service test')"
   ```

3. Check spam/junk folders
4. Verify Gmail app password is correct

## Installation Commands

### Fresh Installation
```bash
# Install all required dependencies
pip install -r requirements.txt

# Or install individually
pip install pyotp==2.9.0
pip install qrcode[pil]==7.4.2
pip install Pillow==10.2.0
```

### Verification Commands
```bash
# Test all 2FA dependencies
python -c "import pyotp, qrcode, PIL; print('All 2FA dependencies OK')"

# Test Flask app integration
python -c "from compass.two_fa import setup; print('2FA module OK')"

# Test QR code generation
python -c "import qrcode; qr = qrcode.QRCode(); qr.add_data('test'); img = qr.make_image(); print('QR generation OK')"
```

## Debug Mode

### Enable Debug Logging
Add to your Flask configuration:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Debug Checks
1. **Check imports**:
   ```bash
   python -c "from compass import create_app; app = create_app(); print('App creation OK')"
   ```

2. **Check database**:
   ```bash
   python -c "from compass.models import User; print('Models OK')"
   ```

3. **Check 2FA routes**:
   ```bash
   python -c "from compass.two_fa import two_fa; print('2FA blueprint OK')"
   ```

## Environment Setup

### Windows-Specific Issues
- Use PowerShell or Command Prompt as Administrator
- Ensure Python is in PATH
- Consider using virtual environment:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  pip install -r requirements.txt
  ```

### Linux/Mac-Specific Issues
- Use `python3` instead of `python` if needed
- Install system dependencies if required:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install python3-dev libjpeg-dev zlib1g-dev
  
  # macOS with Homebrew
  brew install libjpeg zlib
  ```

## Contact Support

If issues persist after following this guide:

1. **Check logs** for specific error messages
2. **Verify environment** configuration
3. **Test components** individually
4. **Create minimal test case** to isolate the issue

### System Information to Provide
- Operating System and version
- Python version (`python --version`)
- Installed package versions (`pip list`)
- Complete error message and stack trace
- Steps to reproduce the issue

---

**Last Updated**: January 2025
**Version**: 1.0
