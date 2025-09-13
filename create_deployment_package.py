#!/usr/bin/env python3
"""
Create a deployment package for AWS Elastic Beanstalk
Excludes unnecessary files and creates a clean ZIP for deployment
"""
import zipfile
import os
import shutil
from pathlib import Path

def create_deployment_zip():
    """Create a deployment ZIP file for AWS Elastic Beanstalk"""
    
    # Files and directories to exclude
    exclude_patterns = {
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '.git',
        '.gitignore',
        'venv',
        'env',
        '.env',
        '.vscode',
        '.idea',
        'instance',
        '*.db',
        '*.sqlite',
        '*.sqlite3',
        'backups',
        '.pytest_cache',
        'node_modules',
        '.DS_Store',
        'Thumbs.db',
        'create_deployment_package.py',
        'compass-deployment.zip'
    }
    
    def should_exclude(file_path):
        """Check if file should be excluded"""
        path = Path(file_path)
        
        # Check each part of the path
        for part in path.parts:
            if any(pattern in part for pattern in exclude_patterns):
                return True
                
        # Check file extensions
        if path.suffix in ['.pyc', '.pyo', '.db', '.sqlite', '.sqlite3']:
            return True
            
        return False
    
    # Create deployment ZIP
    zip_name = 'compass-deployment.zip'
    
    print(f"Creating deployment package: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Remove excluded directories from dirs list to prevent walking into them
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if not should_exclude(file_path):
                    # Add to ZIP with relative path
                    arcname = os.path.relpath(file_path, '.')
                    zipf.write(file_path, arcname)
                    print(f"Added: {arcname}")
    
    file_size = os.path.getsize(zip_name) / (1024 * 1024)  # Size in MB
    print(f"\nDeployment package created: {zip_name}")
    print(f"Size: {file_size:.2f} MB")
    print(f"\nYou can now upload {zip_name} to AWS Elastic Beanstalk!")

if __name__ == "__main__":
    create_deployment_zip()
