# Email Setup Instructions for COMPASS

## Problem
The email verification is failing because Gmail SMTP authentication is not properly configured.

## Solution
You need to set up an **App Password** for the Gmail account `arctic.ncpor@gmail.com`.

## Step-by-Step Setup:

### 1. Enable 2-Factor Authentication on Gmail
- Go to https://myaccount.google.com/
- Log in with `arctic.ncpor@gmail.com`
- Go to "Security" → "2-Step Verification"
- Enable 2FA if not already enabled

### 2. Generate App Password
- In Google Account Security settings
- Go to "2-Step Verification"
- Scroll down to "App passwords"
- Click "App passwords"
- Select "Mail" and "Other (Custom name)"
- Enter "COMPASS NCPOR System"
- Click "Generate"
- **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

### 3. Set Environment Variable
Create a `.env` file in the COMPASS root directory:

```bash
# Email Configuration
MAIL_PASSWORD=your-16-character-app-password-here
```

**Example:**
```bash
MAIL_PASSWORD=abcd efgh ijkl mnop
```

### 4. Alternative: Set Windows Environment Variable
If you don't want to use a .env file:

1. **PowerShell (Temporary):**
```powershell
$env:MAIL_PASSWORD="your-16-character-app-password-here"
```

2. **Windows System Environment Variable (Permanent):**
- Right-click "This PC" → Properties
- Advanced System Settings → Environment Variables
- New System Variable:
  - Name: `MAIL_PASSWORD`
  - Value: `your-16-character-app-password-here`

### 5. Restart the Application
After setting the environment variable:
```bash
python app.py
```

## Testing the Email
To test if email is working:

1. Try to create a new user account
2. Check if the verification email is sent
3. Check the application logs for any email errors

## Troubleshooting

### If Still Not Working:

1. **Check Gmail Security:**
   - Ensure "Less secure app access" is OFF (we're using App Password)
   - Verify 2FA is enabled on the Gmail account

2. **Verify Configuration:**
   ```python
   # Run this to check config:
   python -c "
   from compass import create_app
   app = create_app()
   print('Mail Password Set:', bool(app.config.get('MAIL_PASSWORD')))
   print('Mail Username:', app.config.get('MAIL_USERNAME'))
   "
   ```

3. **Check Application Logs:**
   - Look for email-related errors in the console output
   - Check for authentication failures

4. **Test SMTP Connection:**
   ```python
   # Test SMTP connection
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('arctic.ncpor@gmail.com', 'your-app-password')
   print("SMTP connection successful!")
   server.quit()
   ```

## Security Notes

- **Never commit the app password to version control**
- **Use environment variables only**
- **The app password is specific to COMPASS**
- **You can revoke and regenerate it anytime**

## Email Templates
The system sends professional HTML emails with:
- NCPOR branding
- 6-digit OTP codes
- Security warnings
- 15-minute expiration notices
- Arctic theme styling

Once configured, users will receive beautiful verification emails for:
- Account registration
- Two-factor authentication
- Password resets (if implemented)
