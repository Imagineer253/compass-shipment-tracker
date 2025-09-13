import os
from compass import create_app

app = create_app()

if __name__ == '__main__':
    # Use environment variables for production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    app.run(host=host, port=port, debug=debug_mode)