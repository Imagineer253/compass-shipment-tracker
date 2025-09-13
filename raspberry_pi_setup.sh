#!/bin/bash

# Raspberry Pi COMPASS Setup Script
echo "🍓 Setting up COMPASS on Raspberry Pi..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    sqlite3 \
    nginx \
    supervisor \
    libpq-dev \
    python3-dev \
    build-essential

# Create compass user (optional, for security)
sudo useradd -m -s /bin/bash compass || echo "User compass already exists"

# Create project directory
sudo mkdir -p /opt/compass
sudo chown $USER:$USER /opt/compass

# Clone repository
cd /opt/compass
git clone https://github.com/Imagineer253/compass-shipment-tracker.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create instance directory
mkdir -p instance

# Set up environment file
cat > .env << EOF
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
FLASK_CONFIG=production
DATABASE_URL=sqlite:///instance/compass.db
FLASK_APP=app.py

# Email configuration (update with your settings)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
EOF

# Initialize database
export FLASK_APP=app.py
flask db upgrade

# Create admin user
python scripts/setup_admin.py

echo "✅ COMPASS setup complete!"
echo "🌐 Your app will be available at: http://your-pi-ip:5000"
echo "📱 QR codes will work with: http://your-pi-ip:5000/track/..."
