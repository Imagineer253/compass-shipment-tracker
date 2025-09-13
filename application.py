import os
from compass import create_app

# AWS Elastic Beanstalk expects 'application' variable
application = create_app()

if __name__ == '__main__':
    # For local development
    application.run(debug=False)
