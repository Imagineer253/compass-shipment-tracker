# 🌐 Port Forwarding Setup for Raspberry Pi

## Option B: Router Port Forwarding (Permanent Solution)

### Step 1: Set Static IP for Raspberry Pi

```bash
# Find your Pi's current IP
hostname -I

# Edit dhcpcd.conf for static IP
sudo nano /etc/dhcpcd.conf

# Add these lines (adjust for your network):
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

### Step 2: Router Configuration

1. **Access Router Admin Panel**
   - Usually: http://192.168.1.1 or http://192.168.0.1
   - Login with admin credentials

2. **Set Port Forwarding**
   - Find "Port Forwarding" or "Virtual Servers"
   - Add new rule:
     - **Service Name**: COMPASS
     - **External Port**: 80 (or 8080)
     - **Internal IP**: 192.168.1.100 (your Pi's IP)
     - **Internal Port**: 5000
     - **Protocol**: TCP

3. **Find Your Public IP**
   ```bash
   curl ifconfig.me
   ```

### Step 3: Access Your App

- **Local**: http://192.168.1.100:5000
- **Internet**: http://YOUR_PUBLIC_IP:80
- **QR Codes**: Will use your public IP automatically

### Step 4: Optional - Get Domain Name

1. **Use Free Dynamic DNS** (recommended):
   - Sign up at No-IP.com or DuckDNS.org
   - Get free domain like: compass-tracker.ddns.net
   - Install update client on Pi

2. **Or Buy Domain**:
   - Point A record to your public IP
   - Update when IP changes

## Security Considerations

```bash
# Set up basic firewall
sudo ufw enable
sudo ufw allow 5000/tcp
sudo ufw allow ssh

# Change default SSH port
sudo nano /etc/ssh/sshd_config
# Change Port 22 to Port 2222

# Use strong passwords
passwd  # Change your password
```

## Automatic Startup

```bash
# Create systemd service
sudo nano /etc/systemd/system/compass.service

# Add service configuration:
[Unit]
Description=COMPASS Shipment Tracker
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/compass
Environment=PATH=/opt/compass/venv/bin
ExecStart=/opt/compass/venv/bin/gunicorn --bind 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable compass
sudo systemctl start compass
sudo systemctl status compass
```
