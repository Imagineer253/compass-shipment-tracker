from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def get_package_type_display_name(package_type):
    """Convert package type code to display name"""
    package_type_mapping = {
        'cardboard_box': 'Cardboard Box',
        'plastic_crate': 'Plastic Crate',
        'metal_trunk': 'Metal Trunk',
        'zarges': 'Zarges',
        'pelican_case': 'Pelican Case',
        'other': 'Other',
        # Legacy support for old values
        'box': 'Cardboard Box',
        'carton': 'Plastic Crate',
        'crate': 'Metal Trunk'
    }
    return package_type_mapping.get(package_type, package_type.title())

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function 