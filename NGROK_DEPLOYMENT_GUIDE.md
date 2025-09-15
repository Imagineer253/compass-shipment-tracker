# 🌐 COMPASS ngrok Deployment Guide

Complete guide to hosting COMPASS on your laptop server with global access via ngrok.

## 📋 Prerequisites

- **Server laptop** with reliable internet connection
- **Python 3.11** installed (recommended version)
- **ngrok account** (free tier works, paid for custom subdomain)
- **Gmail account** for email services

## 🚀 Quick Start

### 1. Server Laptop Setup

```bash
# 1. Copy COMPASS project to your server laptop
# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run production setup
python setup_production.py
```

### 2. Configure Environment

Edit `production.env`:

```env
# Required: Change these values
SECRET_KEY=your-generated-secret-key-from-setup
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
ADMIN_EMAIL=admin@yourcompany.com
ADMIN_PASSWORD=SecurePassword123!

# Optional: Customize these
FLASK_ENV=production
HOST=0.0.0.0
PORT=5000
```

### 3. Email Setup (Gmail)

1. **Enable 2FA** on your Gmail account
2. **Generate App Password:**
   - Gmail → Settings → Security → 2-Step Verification → App passwords
   - Select "Mail" and generate password
3. **Update production.env** with the app password

### 4. ngrok Setup

```bash
# 1. Download ngrok from https://ngrok.com
# 2. Sign up and get authtoken
# 3. Authenticate
ngrok authtoken YOUR_AUTHTOKEN

# 4. Edit ngrok.yml with your authtoken
# 5. For custom subdomain (paid plan), update subdomain field
```

### 5. Start Services

```bash
# Terminal 1: Start COMPASS server
python start_server.py

# Terminal 2: Start ngrok tunnel
ngrok start compass

# Alternative: Quick start without config file
ngrok http 5000
```

## 🌍 Access Your App

After starting ngrok, you'll see:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:5000
```

**Your COMPASS app is now accessible worldwide at:** `https://abc123.ngrok.io`

## 📱 QR Code Updates

1. **Login as admin:** `https://abc123.ngrok.io/login`
2. **Go to QR Codes management:** Admin Dashboard → QR Codes
3. **Bulk regenerate** all QR codes with new domain
4. **Download updated QR codes** for reprinting

## 🔧 Production Optimization

### Auto-Start Scripts

**Windows (start_compass.bat):**
```batch
@echo off
cd /d "C:\path\to\compass"
call venv\Scripts\activate
start /b python start_server.py
start /b ngrok start compass
echo COMPASS server started!
pause
```

**Linux/Mac (start_compass.sh):**
```bash
#!/bin/bash
cd /path/to/compass
source venv/bin/activate
python start_server.py &
ngrok start compass &
echo "COMPASS server started!"
```

### Monitoring & Logs

- **ngrok web interface:** http://localhost:4040
- **Server logs:** Check terminal output
- **Email testing:** Use test_email.py script

## 🛡️ Security Considerations

### ✅ Enabled by Default
- HTTPS enforced by ngrok
- CSRF protection
- Session security
- Input validation

### 🔒 Additional Security (Optional)
- **ngrok password protection:**
  ```yaml
  auth: "username:password"
  ```
- **IP whitelist** (ngrok paid plans)
- **Custom domain** for consistent URLs

## 🔄 Maintenance

### Daily Operations
- **Monitor server laptop** uptime
- **Check ngrok connection** status
- **Backup database** regularly

### Updates
```bash
# Stop services
# Update code
git pull origin main
pip install -r requirements.txt

# Update database
python setup_production.py

# Restart services
python start_server.py
ngrok start compass
```

## 🆘 Troubleshooting

### Common Issues

**ngrok tunnel failed:**
- Check internet connection
- Verify authtoken
- Try different region: `ngrok http 5000 --region eu`

**Email not working:**
- Verify Gmail app password
- Check firewall settings
- Test with: `python test_email.py`

**Database errors:**
- Run: `python setup_production.py`
- Check file permissions
- Verify database path

**QR codes not working:**
- Regenerate with new domain
- Check QR code image paths
- Verify static file serving

### Getting Help

1. **Check logs** in terminal output
2. **ngrok status:** http://localhost:4040
3. **Test locally:** http://localhost:5000
4. **Email admin:** Error details to admin email

## 💡 Pro Tips

- **Use paid ngrok** for custom subdomain
- **Keep server laptop always on** and connected
- **Set up automatic backups** of database and uploads
- **Monitor bandwidth** usage (ngrok free tier limits)
- **Use UPS** for power backup on server laptop

## 🎯 Success Checklist

- ✅ Server laptop configured and running
- ✅ ngrok tunnel active and accessible
- ✅ Admin account working
- ✅ Email notifications functional
- ✅ QR codes generated with correct domain
- ✅ Package tracking working from mobile
- ✅ Shipment creation and management operational

Your COMPASS system is now globally accessible! 🌍🎉
