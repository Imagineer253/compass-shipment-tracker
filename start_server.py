#!/usr/bin/env python3
"""
Production server startup script for COMPASS
Optimized for ngrok hosting
"""
import os
import sys
from dotenv import load_dotenv
from compass import create_app

def start_production_server():
    """Start the COMPASS server in production mode"""
    
    # Load production environment variables
    if os.path.exists('production.env'):
        load_dotenv('production.env')
        print("✅ Loaded production.env configuration")
    else:
        load_dotenv()
        print("⚠️  Using default .env configuration")
    
    # Create Flask app
    app = create_app()
    
    # Production settings
    host = os.environ.get('HOST', '0.0.0.0')  # Allow external connections
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"""
🧭 COMPASS Server Starting...
📡 Host: {host}
🔌 Port: {port}
🌍 Environment: {'Development' if debug else 'Production'}
📱 Ready for ngrok tunneling!

🚀 Access locally: http://localhost:{port}
🌐 After ngrok setup: https://your-subdomain.ngrok.io
""")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,  # Handle multiple requests
            use_reloader=False  # Disable in production
        )
    except KeyboardInterrupt:
        print("\n👋 COMPASS server stopped gracefully")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_production_server()
