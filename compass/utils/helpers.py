from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from datetime import datetime

def get_package_type_display_name(package_type, form_data=None, package_num=None):
    """Convert package type code to display name, handling 'other' type with custom input"""
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
    
    # If package type is 'other' and we have form_data and package_num, get the custom type
    if package_type == 'other' and form_data and package_num:
        other_type = form_data.get(f'package_{package_num}_other_type', '')
        if other_type:
            return other_type
    
    return package_type_mapping.get(package_type, package_type.title())

def generate_file_reference_number(shipment, acknowledging_admin):
    """
    Generate file reference number in format: ARC/YYYY/MMM/Admin_Unique_ID/Unique_ID-or-CMB/Serial
    
    Args:
        shipment: Shipment object
        acknowledging_admin: User object of the admin acknowledging the shipment
        
    Returns:
        str: Generated file reference number
    """
    from ..models import FileReferenceCounter
    
    # Get current date components
    current_date = datetime.now()
    year = current_date.strftime('%Y')
    month = current_date.strftime('%b').upper()  # JAN, FEB, MAR, etc.
    
    # Get admin's unique ID
    admin_unique_id = acknowledging_admin.unique_id
    
    # Determine the shipment identifier part
    if shipment.is_combined:
        # For combined shipments, use CMB
        shipment_identifier = "CMB"
    else:
        # For regular shipments, use the requester's unique ID
        # Get the requester's unique ID from the shipment creator
        shipment_identifier = shipment.created_by_user.unique_id
    
    # Get next serial number for file reference
    serial_number = FileReferenceCounter.get_next_file_reference_serial()
    
    # Format: ARC/YYYY/MMM/Admin_Unique_ID/Unique_ID-or-CMB/Serial
    file_reference_number = f"ARC/{year}/{month}/{admin_unique_id}/{shipment_identifier}/{serial_number}"
    
    return file_reference_number

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function 