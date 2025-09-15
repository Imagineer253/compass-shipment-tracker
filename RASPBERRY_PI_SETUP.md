# 🍓 **Raspberry Pi Production Setup Guide**

## **🎯 Objective**
Set up COMPASS web application on Raspberry Pi with:
- ✅ **Automatic startup** on boot
- ✅ **Auto-recovery** after power cuts
- ✅ **Persistent ngrok tunnel** with same URL
- ✅ **24/7 operation** reliability

---

## **📋 Prerequisites**
- Raspberry Pi (3B+ or newer recommended)
- Raspberry Pi OS installed
- Internet connection
- COMPASS project folder copied to Pi
- ngrok account with authtoken

---

## **🚀 Step-by-Step Setup**

### **Step 1: System Update & Python Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
sudo apt install -y build-essential libffi-dev libssl-dev
sudo apt install -y nginx supervisor git curl wget

# Install ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

### **Step 2: Project Setup**
```bash
# Navigate to your COMPASS folder
cd /home/pi/COMPASS

# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p compass/static/uploads
mkdir -p compass/static/qrcodes
mkdir -p logs
```

### **Step 3: Environment Configuration**
```bash
# Create production environment file
cat > .env << 'EOF'
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here-change-this
DATABASE_URL=sqlite:///instance/compass.db

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# ngrok Configuration
NGROK_AUTHTOKEN=your_ngrok_authtoken_here
NGROK_DOMAIN=your-custom-domain.ngrok.io

# Production Settings
HOST=0.0.0.0
PORT=5000
DEBUG=False
EOF

# Make environment file readable only by owner
chmod 600 .env
```

### **Step 4: Database Initialization**
```bash
# Activate virtual environment
source venv/bin/activate

# Initialize database
python setup_production.py

# Create admin user (follow prompts)
python scripts/setup_main_admin.py
```

### **Step 5: ngrok Setup**
```bash
# Configure ngrok with your authtoken
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN

# Create ngrok configuration
mkdir -p ~/.config/ngrok
cat > ~/.config/ngrok/ngrok.yml << 'EOF'
version: "2"
authtoken: YOUR_NGROK_AUTHTOKEN
tunnels:
  compass:
    addr: 5000
    proto: http
    domain: your-domain.ngrok.io  # If you have a custom domain
    # OR use this for random domain:
    # subdomain: compass-tracker
EOF
```

### **Step 6: Systemd Service for Flask App**
```bash
# Create Flask service file
sudo tee /etc/systemd/system/compass.service << 'EOF'
[Unit]
Description=COMPASS Flask Application
After=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/COMPASS
Environment=PATH=/home/pi/COMPASS/venv/bin
ExecStart=/home/pi/COMPASS/venv/bin/python app.py
Restart=always
RestartSec=5
StandardOutput=append:/home/pi/COMPASS/logs/compass.log
StandardError=append:/home/pi/COMPASS/logs/compass_error.log

[Install]
WantedBy=multi-user.target
EOF
```

### **Step 7: Systemd Service for ngrok**
```bash
# Create ngrok service file
sudo tee /etc/systemd/system/ngrok.service << 'EOF'
[Unit]
Description=ngrok tunnel for COMPASS
After=network.target compass.service
Requires=compass.service

[Service]
Type=simple
User=pi
Group=pi
ExecStart=/usr/local/bin/ngrok start compass
Restart=always
RestartSec=10
StandardOutput=append:/home/pi/COMPASS/logs/ngrok.log
StandardError=append:/home/pi/COMPASS/logs/ngrok_error.log

[Install]
WantedBy=multi-user.target
EOF
```

### **Step 8: Enable Auto-Startup Services**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services for auto-start
sudo systemctl enable compass.service
sudo systemctl enable ngrok.service

# Start services
sudo systemctl start compass.service
sudo systemctl start ngrok.service

# Check status
sudo systemctl status compass.service
sudo systemctl status ngrok.service
```

### **Step 9: Monitoring & Log Setup**
```bash
# Create log rotation
sudo tee /etc/logrotate.d/compass << 'EOF'
/home/pi/COMPASS/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    create 644 pi pi
}
EOF

# Create monitoring script
cat > /home/pi/COMPASS/monitor.sh << 'EOF'
#!/bin/bash
cd /home/pi/COMPASS

# Check if services are running
if ! systemctl is-active --quiet compass.service; then
    echo "$(date): COMPASS service not running, restarting..." >> logs/monitor.log
    sudo systemctl restart compass.service
fi

if ! systemctl is-active --quiet ngrok.service; then
    echo "$(date): ngrok service not running, restarting..." >> logs/monitor.log
    sudo systemctl restart ngrok.service
fi

# Log current status
echo "$(date): Services checked - COMPASS: $(systemctl is-active compass.service), ngrok: $(systemctl is-active ngrok.service)" >> logs/monitor.log
EOF

chmod +x /home/pi/COMPASS/monitor.sh

# Add to crontab for monitoring every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/pi/COMPASS/monitor.sh") | crontab -
```

---

## **🔧 Management Commands**

### **Service Control:**
```bash
# Start services
sudo systemctl start compass.service ngrok.service

# Stop services
sudo systemctl stop compass.service ngrok.service

# Restart services
sudo systemctl restart compass.service ngrok.service

# Check status
sudo systemctl status compass.service ngrok.service

# View logs
sudo journalctl -u compass.service -f
sudo journalctl -u ngrok.service -f
```

### **Application Management:**
```bash
# Navigate to project
cd /home/pi/COMPASS

# Activate virtual environment
source venv/bin/activate

# Update database
flask db upgrade

# Check application logs
tail -f logs/compass.log
tail -f logs/ngrok.log
```

### **ngrok URL Management:**
```bash
# Get current ngrok URL
curl -s http://localhost:4040/api/tunnels | python3 -m json.tool

# Or check ngrok dashboard at:
# http://localhost:4040
```

---

## **🛡️ Security & Performance**

### **Firewall Setup:**
```bash
# Install and configure ufw
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 5000
sudo ufw enable
```

### **Performance Optimization:**
```bash
# Increase file limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize Pi for 24/7 operation
echo "gpu_mem=16" | sudo tee -a /boot/config.txt
```

---

## **📱 QR Code URL Persistence**

### **Fixed Domain Option (Recommended):**
1. **Get ngrok Pro account** for custom domains
2. **Set fixed domain** in ngrok.yml
3. **QR codes remain valid** permanently

### **Dynamic Domain Backup:**
1. **QR codes point to** a redirect service
2. **Update redirect target** when ngrok URL changes
3. **Implement URL update** webhook

---

## **🔄 Automatic Recovery Process**

### **Power Cut Recovery:**
1. **Pi boots up** → systemd starts
2. **compass.service** → Flask app starts
3. **ngrok.service** → Tunnel establishes
4. **Monitor script** → Checks every 5 minutes
5. **Auto-restart** → If any service fails

### **Network Issues:**
- **ngrok auto-reconnects** when internet returns
- **Flask app continues** serving locally
- **Services restart** if connection fails

---

## **📊 Monitoring Dashboard**

### **Check System Health:**
```bash
# Quick status check
systemctl is-active compass.service ngrok.service

# Resource usage
htop

# Disk space
df -h

# Application logs
tail -n 50 logs/compass.log
```

### **Web Monitoring:**
- **Local:** http://localhost:5000
- **ngrok Dashboard:** http://localhost:4040
- **Public URL:** Your ngrok URL

---

## **🚨 Troubleshooting**

### **Common Issues:**

1. **Service Won't Start:**
   ```bash
   sudo journalctl -u compass.service --no-pager
   sudo journalctl -u ngrok.service --no-pager
   ```

2. **Database Issues:**
   ```bash
   cd /home/pi/COMPASS
   source venv/bin/activate
   python -c "from compass import create_app; create_app()"
   ```

3. **ngrok Connection Issues:**
   ```bash
   ngrok config check
   ngrok diagnose
   ```

4. **Memory Issues:**
   ```bash
   free -h
   sudo systemctl restart compass.service
   ```

---

## **✅ Final Checklist**

- [ ] System updated and dependencies installed
- [ ] Python 3.11 and virtual environment set up
- [ ] COMPASS project configured with .env
- [ ] Database initialized with admin user
- [ ] ngrok configured with authtoken
- [ ] systemd services created and enabled
- [ ] Services started and running
- [ ] Monitoring script active
- [ ] Firewall configured
- [ ] QR codes tested and working
- [ ] Power cut recovery tested

**🎉 Your COMPASS application should now be running 24/7 with automatic recovery!**
