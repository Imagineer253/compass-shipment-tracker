from flask import current_app
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from urllib.parse import urlparse

def init_db():
    """Initialize the database - create it if it doesn't exist"""
    
    # Get database URL from config
    db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
    
    # Parse the URL to get database name
    url = urlparse(db_url)
    db_name = url.path.lstrip('/')
    
    # Create URL without database name for initial connection
    root_url = f"{url.scheme}://{url.username}:{url.password}@{url.hostname}"
    if url.port:
        root_url += f":{url.port}"
    
    # Create engine to connect without database specified
    engine = create_engine(root_url)
    
    try:
        # Try to connect to the database
        with engine.connect() as conn:
            # Check if database exists
            databases = conn.execute(sa.text("SHOW DATABASES")).fetchall()
            if (db_name,) not in databases:
                # Create database if it doesn't exist
                conn.execute(sa.text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
                print(f"Database '{db_name}' created successfully!")
            
            # Switch to the database
            conn.execute(sa.text(f"USE {db_name}"))
            
    except OperationalError as e:
        print(f"Error connecting to database: {e}")
        raise
    finally:
        engine.dispose() 