# 🍓 **COMPASS Setup Instructions for User 'sarab'**

## **📍 Your Current Setup**
- **Username:** `sarab`
- **Hostname:** `sarab` (sarab@sarab)
- **COMPASS Location:** `/home/sarab/Desktop/COMPASS`
- **Home Directory:** `/home/sarab`

---

## **🚀 Quick Setup Steps**

### **1. Navigate to COMPASS Folder**
```bash
cd ~/Desktop/COMPASS
```

### **2. Make Setup Script Executable**
```bash
chmod +x rpi_quick_setup.sh
```

### **3. Run the Setup Script**
```bash
./rpi_quick_setup.sh
```

The script will automatically:
- ✅ Detect your username (`sarab`)
- ✅ Find COMPASS folder on Desktop
- ✅ Install all dependencies
- ✅ Create services with correct user permissions
- ✅ Set up auto-startup

---

## **⚙️ What Changed for Your Setup**

### **🔧 User Configuration:**
- **Script adapted** for user `sarab` instead of `pi`
- **Paths updated** to `/home/sarab/Desktop/COMPASS`
- **Services configured** to run as `sarab` user
- **Permissions set** for `sarab` user and group

### **📁 Directory Detection:**
The script will automatically check these locations:
1. `/home/sarab/Desktop/COMPASS` ✅ (your current location)
2. `/home/sarab/COMPASS`
3. `/home/sarab/Desktop/compass`
4. `/home/sarab/compass`

### **🔐 Service Configuration:**
- **COMPASS service:** Runs as `sarab:sarab`
- **ngrok service:** Runs as `sarab:sarab`  
- **Log files:** Owned by `sarab`
- **Monitoring:** Uses your home directory

---

## **📋 Step-by-Step Process**

### **Step 1: Preparation**
```bash
# Ensure you're in the right directory
pwd
# Should show: /home/sarab/Desktop/COMPASS

# List files to confirm
ls -la
# Should see: app.py, compass/, requirements.txt, etc.
```

### **Step 2: Run Setup**
```bash
# Make script executable
chmod +x rpi_quick_setup.sh

# Run the setup
./rpi_quick_setup.sh
```

### **Step 3: Configure Environment**
After setup completes, you'll need to:

```bash
# Edit environment variables
nano .env
```

**Update these values in .env:**
```bash
SECRET_KEY=your-super-secret-key-change-this
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
NGROK_AUTHTOKEN=your_ngrok_authtoken_here
```

### **Step 4: Setup ngrok**
```bash
# Add your ngrok authtoken
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

### **Step 5: Create Admin User**
```bash
# Activate virtual environment
source venv/bin/activate

# Create admin user
python scripts/setup_main_admin.py
```

### **Step 6: Start Services**
```bash
# Start both services
sudo systemctl start compass.service ngrok.service

# Check they're running
sudo systemctl status compass.service ngrok.service
```

### **Step 7: Get Your Public URL**
```bash
# Get ngrok tunnel URL
curl -s http://localhost:4040/api/tunnels | python3 -m json.tool

# Look for "public_url" in the output
```

---

## **🔧 Service Management Commands**

### **Check Status:**
```bash
sudo systemctl status compass.service ngrok.service
```

### **Restart Services:**
```bash
sudo systemctl restart compass.service ngrok.service
```

### **View Logs:**
```bash
# COMPASS logs
tail -f /home/sarab/Desktop/COMPASS/logs/compass.log

# ngrok logs  
tail -f /home/sarab/Desktop/COMPASS/logs/ngrok.log

# System service logs
sudo journalctl -u compass.service -f
sudo journalctl -u ngrok.service -f
```

### **Stop Services:**
```bash
sudo systemctl stop compass.service ngrok.service
```

---

## **📱 Testing Your Setup**

### **1. Local Access:**
```bash
# Check local website
curl http://localhost:5000
```

### **2. Public Access:**
```bash
# Get public URL
curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | cut -d'"' -f4
```

### **3. QR Code Test:**
- **Visit:** Your ngrok URL
- **Login** with admin credentials
- **Go to:** Admin Panel → QR Codes
- **Test:** Generate and scan a QR code

---

## **🔄 Auto-Startup Verification**

### **Test Power Recovery:**
```bash
# Reboot to test auto-startup
sudo reboot
```

**After reboot, check:**
```bash
# Services should be running automatically
sudo systemctl status compass.service ngrok.service

# Should both show "active (running)"
```

---

## **🚨 Troubleshooting**

### **If Script Fails:**
```bash
# Check what went wrong
sudo journalctl -u compass.service --no-pager
sudo journalctl -u ngrok.service --no-pager
```

### **If Services Don't Start:**
```bash
# Manual start for debugging
cd ~/Desktop/COMPASS
source venv/bin/activate
python app.py
```

### **If ngrok Fails:**
```bash
# Check ngrok configuration
ngrok config check

# Test ngrok manually
ngrok http 5000
```

### **Permission Issues:**
```bash
# Fix ownership if needed
sudo chown -R sarab:sarab /home/sarab/Desktop/COMPASS
```

---

## **✅ Success Indicators**

Your setup is working when:

1. **✅ Both services active:**
   ```bash
   sudo systemctl is-active compass.service ngrok.service
   # Should output: active active
   ```

2. **✅ Website accessible:**
   - Local: http://localhost:5000
   - Public: Your ngrok URL

3. **✅ QR codes working:**
   - Generate QR in admin panel
   - Scan with phone
   - Should open tracking page

4. **✅ Auto-recovery working:**
   - Reboot Pi: `sudo reboot`
   - Services start automatically
   - Same ngrok URL restored

---

## **🎉 Final Result**

After successful setup:
- **🌐 COMPASS accessible** via ngrok URL
- **🔄 Auto-starts** on boot
- **📱 QR codes functional** from anywhere
- **🛡️ Secure** and monitored
- **⚡ Resilient** to power cuts

**Your COMPASS installation will be production-ready and accessible 24/7!** 🚀

---

## **📞 Need Help?**

If you encounter any issues:
1. **Check logs:** `tail -f ~/Desktop/COMPASS/logs/compass.log`
2. **Verify services:** `sudo systemctl status compass.service ngrok.service`
3. **Test manually:** `cd ~/Desktop/COMPASS && source venv/bin/activate && python app.py`

**The setup script has been customized for your exact configuration!** ✨
