#!/bin/bash
source /var/app/venv/*/bin/activate
cd /var/app/current
export FLASK_APP=app.py

# Run database migrations
python -m flask db upgrade

# Create admin user if doesn't exist
python scripts/setup_admin.py || echo "Admin setup completed or already exists"

# Create necessary directories
mkdir -p compass/static/uploads/profile_pictures
mkdir -p compass/static/uploads/passports  
mkdir -p compass/static/qrcodes
chmod 755 compass/static/uploads/profile_pictures
chmod 755 compass/static/uploads/passports
chmod 755 compass/static/qrcodes
