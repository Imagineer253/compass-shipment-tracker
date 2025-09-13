#!/bin/bash

# COMPASS Raspberry Pi Startup Script
echo "🍓 Starting COMPASS on Raspberry Pi..."

# Navigate to project directory
cd /opt/compass

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export FLASK_APP=app.py
export FLASK_CONFIG=production

# Run database migrations
flask db upgrade

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "🚀 Starting COMPASS server..."
echo "📱 Local access: http://${LOCAL_IP}:5000"
echo "🌐 Admin dashboard: http://${LOCAL_IP}:5000/dashboard"
echo "📋 QR tracking: http://${LOCAL_IP}:5000/track"
echo ""
echo "🛑 Press Ctrl+C to stop the server"

# Start the Flask application
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app
