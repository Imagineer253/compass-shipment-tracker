import os
import sys
import logging

# Add the current directory to Python path
sys.path.insert(0, '/var/app/current')

from compass import create_app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Elastic Beanstalk expects 'application' variable
try:
    application = create_app()
    logger.info("Flask application created successfully")
except Exception as e:
    logger.error(f"Failed to create Flask application: {e}")
    raise

if __name__ == '__main__':
    # For local development
    application.run(debug=False, host='0.0.0.0', port=5000)
