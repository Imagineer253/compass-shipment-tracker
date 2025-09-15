#!/bin/bash

# 🍓 COMPASS Raspberry Pi Quick Setup Script
# Run this script on your Raspberry Pi to set up COMPASS automatically

set -e  # Exit on any error

echo "🍓 Starting COMPASS Raspberry Pi Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as correct user (allow any user, but warn about paths)
CURRENT_USER=$(whoami)
HOME_DIR="/home/$CURRENT_USER"
print_status "Running as user: $CURRENT_USER"
print_status "Home directory: $HOME_DIR"

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip \
    build-essential libffi-dev libssl-dev nginx supervisor git curl wget \
    htop ufw

# Install ngrok
print_status "Installing ngrok..."
if ! command -v ngrok &> /dev/null; then
    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
    sudo apt update && sudo apt install ngrok -y
fi

# Check if COMPASS directory exists (try multiple common locations)
COMPASS_LOCATIONS=(
    "$HOME_DIR/Desktop/COMPASS"
    "$HOME_DIR/COMPASS" 
    "$HOME_DIR/Desktop/compass"
    "$HOME_DIR/compass"
)

COMPASS_DIR=""
for location in "${COMPASS_LOCATIONS[@]}"; do
    if [ -d "$location" ]; then
        COMPASS_DIR="$location"
        print_success "Found COMPASS directory at: $COMPASS_DIR"
        break
    fi
done

if [ -z "$COMPASS_DIR" ]; then
    print_error "COMPASS directory not found in any of these locations:"
    for location in "${COMPASS_LOCATIONS[@]}"; do
        print_error "  - $location"
    done
    print_error "Please ensure COMPASS folder is in one of these locations"
    exit 1
fi

cd "$COMPASS_DIR"

# Create virtual environment
print_status "Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p compass/static/uploads
mkdir -p compass/static/qrcodes
mkdir -p logs
mkdir -p instance

# Create .env file (user will need to fill in values)
print_status "Creating environment configuration template..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=CHANGE-THIS-TO-A-SECURE-SECRET-KEY
DATABASE_URL=sqlite:///instance/compass.db

# Email Configuration (Update these)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# ngrok Configuration (Update these)
NGROK_AUTHTOKEN=your_ngrok_authtoken_here

# Production Settings
HOST=0.0.0.0
PORT=5000
DEBUG=False
EOF
    chmod 600 .env
    print_warning "Created .env file template. Please edit it with your actual values:"
    print_warning "nano .env"
fi

# Initialize database
print_status "Initializing database..."
if [ -f "setup_production.py" ]; then
    python setup_production.py
else
    # Fallback database initialization
    python -c "
from compass import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
fi

# Create systemd service for COMPASS
print_status "Creating COMPASS systemd service..."
sudo tee /etc/systemd/system/compass.service > /dev/null << EOF
[Unit]
Description=COMPASS Flask Application
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$COMPASS_DIR
Environment=PATH=$COMPASS_DIR/venv/bin
ExecStart=$COMPASS_DIR/venv/bin/python app.py
Restart=always
RestartSec=5
StandardOutput=append:$COMPASS_DIR/logs/compass.log
StandardError=append:$COMPASS_DIR/logs/compass_error.log

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for ngrok
print_status "Creating ngrok systemd service..."
sudo tee /etc/systemd/system/ngrok.service > /dev/null << EOF
[Unit]
Description=ngrok tunnel for COMPASS
After=network.target compass.service
Requires=compass.service

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
ExecStart=/usr/bin/ngrok http 5000
Restart=always
RestartSec=10
StandardOutput=append:$COMPASS_DIR/logs/ngrok.log
StandardError=append:$COMPASS_DIR/logs/ngrok_error.log

[Install]
WantedBy=multi-user.target
EOF

# Create monitoring script
print_status "Creating monitoring script..."
cat > monitor.sh << EOF
#!/bin/bash
cd "$COMPASS_DIR"

# Check if services are running
if ! systemctl is-active --quiet compass.service; then
    echo "\$(date): COMPASS service not running, restarting..." >> logs/monitor.log
    sudo systemctl restart compass.service
fi

if ! systemctl is-active --quiet ngrok.service; then
    echo "\$(date): ngrok service not running, restarting..." >> logs/monitor.log
    sudo systemctl restart ngrok.service
fi

# Log current status
echo "\$(date): Services checked - COMPASS: \$(systemctl is-active compass.service), ngrok: \$(systemctl is-active ngrok.service)" >> logs/monitor.log
EOF

chmod +x monitor.sh

# Add monitoring to crontab
print_status "Setting up monitoring cron job..."
(crontab -l 2>/dev/null | grep -v "monitor.sh"; echo "*/5 * * * * $COMPASS_DIR/monitor.sh") | crontab -

# Set up log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/compass > /dev/null << EOF
$COMPASS_DIR/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    create 644 $CURRENT_USER $CURRENT_USER
}
EOF

# Configure firewall
print_status "Configuring firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 5000
sudo ufw --force enable

# Enable and start services
print_status "Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable compass.service
sudo systemctl enable ngrok.service

print_success "Setup completed! 🎉"
print_warning ""
print_warning "⚠️  IMPORTANT NEXT STEPS:"
print_warning "1. Edit .env file with your actual values:"
print_warning "   nano .env"
print_warning ""
print_warning "2. Set up ngrok authtoken:"
print_warning "   ngrok config add-authtoken YOUR_AUTHTOKEN"
print_warning ""
print_warning "3. Create admin user:"
print_warning "   source venv/bin/activate"
print_warning "   python scripts/setup_main_admin.py"
print_warning ""
print_warning "4. Start services:"
print_warning "   sudo systemctl start compass.service ngrok.service"
print_warning ""
print_warning "5. Check status:"
print_warning "   sudo systemctl status compass.service ngrok.service"
print_warning ""
print_warning "6. Get ngrok URL:"
print_warning "   curl -s http://localhost:4040/api/tunnels"
print_warning ""

echo ""
print_success "COMPASS is ready for production! 🚀"
