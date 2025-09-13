#!/bin/bash

# Install ngrok for public internet access
echo "🌐 Setting up ngrok for internet access..."

# Download and install ngrok
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# You'll need to get an auth token from https://ngrok.com/
echo "📋 Steps to complete setup:"
echo "1. Go to https://ngrok.com/ and sign up"
echo "2. Get your auth token from dashboard"
echo "3. Run: ngrok config add-authtoken YOUR_TOKEN"
echo "4. Start tunnel: ngrok http 5000"
echo ""
echo "Your app will be accessible at: https://XXXXX.ngrok.io"
echo "QR codes will automatically use the ngrok URL!"
