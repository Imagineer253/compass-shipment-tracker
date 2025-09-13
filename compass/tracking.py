"""
Public tracking blueprint for QR code package tracking
No authentication required - public access for package tracking
"""
from flask import Blueprint, render_template, request, jsonify, abort, current_app
from .models import PackageQRCode, Shipment, User
from datetime import datetime
import re

tracking = Blueprint('tracking', __name__)

@tracking.route('/track/<tracking_code>')
def track_package(tracking_code):
    """
    Public package tracking page - no authentication required
    Displays comprehensive package and shipment information
    
    Args:
        tracking_code: 12-character unique tracking code
    """
    try:
        # Validate tracking code format (12 alphanumeric characters)
        if not re.match(r'^[A-Z0-9]{12}$', tracking_code.upper()):
            return render_template('tracking/track_error.html', 
                                 error_type='invalid_format',
                                 message='Invalid tracking code format. Please check your QR code.')
        
        # Find package by tracking code
        package = PackageQRCode.query.filter_by(unique_code=tracking_code.upper()).first()
        
        if not package:
            return render_template('tracking/track_error.html',
                                 error_type='not_found',
                                 message='Package not found. Please verify your tracking code.')
        
        # Get comprehensive package information
        package_info = package.get_package_info()
        
        # Add additional computed information
        package_info['tracking_url'] = request.url
        package_info['qr_code_url'] = None
        
        # Get QR code image URL if available
        if package.qr_image_path:
            package_info['qr_code_url'] = f"/{package.qr_image_path}"
        
        # Format dates for display
        package_info['created_at_formatted'] = package.created_at.strftime('%B %d, %Y at %I:%M %p')
        package_info['shipment']['created_at_formatted'] = package.shipment.created_at.strftime('%B %d, %Y at %I:%M %p')
        
        if package.shipment.acknowledged_at:
            package_info['shipment']['acknowledged_at_formatted'] = package.shipment.acknowledged_at.strftime('%B %d, %Y at %I:%M %p')
        
        # Get shipment form data for additional details
        shipment_details = {}
        if package.shipment.form_data:
            import json
            try:
                form_data = json.loads(package.shipment.form_data)
                shipment_details = {
                    'requester_name': form_data.get('requester_name'),
                    'expedition_year': form_data.get('expedition_year'),
                    'batch_number': form_data.get('batch_number'),
                    'mode_of_transport': form_data.get('mode_of_transport'),
                    'port_of_loading': form_data.get('port_of_loading'),
                    'port_of_discharge': form_data.get('port_of_discharge'),
                    'destination_country': form_data.get('destination_country'),
                    'departure_date': form_data.get('departure_date'),
                    'arrival_date': form_data.get('arrival_date')
                }
            except json.JSONDecodeError:
                pass
        
        # Add shipment details to package info
        package_info['shipment_details'] = shipment_details
        
        # Get status color and icon
        status_info = _get_status_display_info(package.shipment.status)
        package_info['status_info'] = status_info
        
        return render_template('tracking/track_package.html', 
                             package=package_info,
                             tracking_code=tracking_code.upper())
    
    except Exception as e:
        current_app.logger.error(f"Error tracking package {tracking_code}: {str(e)}")
        return render_template('tracking/track_error.html',
                             error_type='system_error',
                             message='System error occurred. Please try again later.')

@tracking.route('/api/track/<tracking_code>')
def api_track_package(tracking_code):
    """
    API endpoint for package tracking - returns JSON data
    
    Args:
        tracking_code: 12-character unique tracking code
        
    Returns:
        JSON response with package information
    """
    try:
        # Validate tracking code format
        if not re.match(r'^[A-Z0-9]{12}$', tracking_code.upper()):
            return jsonify({
                'success': False,
                'error': 'invalid_format',
                'message': 'Invalid tracking code format'
            }), 400
        
        # Find package by tracking code
        package = PackageQRCode.query.filter_by(unique_code=tracking_code.upper()).first()
        
        if not package:
            return jsonify({
                'success': False,
                'error': 'not_found',
                'message': 'Package not found'
            }), 404
        
        # Get package information
        package_info = package.get_package_info()
        
        # Add status display info
        status_info = _get_status_display_info(package.shipment.status)
        package_info['status_info'] = status_info
        
        # Add timestamps in ISO format for API
        package_info['created_at_iso'] = package.created_at.isoformat()
        package_info['shipment']['created_at_iso'] = package.shipment.created_at.isoformat()
        
        if package.shipment.acknowledged_at:
            package_info['shipment']['acknowledged_at_iso'] = package.shipment.acknowledged_at.isoformat()
        
        return jsonify({
            'success': True,
            'package': package_info
        })
    
    except Exception as e:
        current_app.logger.error(f"API error tracking package {tracking_code}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'system_error',
            'message': 'System error occurred'
        }), 500

@tracking.route('/track')
def track_home():
    """
    Public tracking home page with tracking code input
    """
    return render_template('tracking/track_home.html')

@tracking.route('/track/search', methods=['POST'])
def track_search():
    """
    Handle tracking code search from the tracking home page
    """
    tracking_code = request.form.get('tracking_code', '').strip().upper()
    
    if not tracking_code:
        return render_template('tracking/track_home.html', 
                             error='Please enter a tracking code')
    
    # Validate and redirect to tracking page
    if not re.match(r'^[A-Z0-9]{12}$', tracking_code):
        return render_template('tracking/track_home.html',
                             error='Invalid tracking code format. Please enter a 12-character code.')
    
    # Redirect to the actual tracking page
    from flask import redirect, url_for
    return redirect(url_for('tracking.track_package', tracking_code=tracking_code))

def _get_status_display_info(status):
    """
    Get display information for shipment status
    
    Args:
        status: Shipment status string
        
    Returns:
        Dictionary with color, icon, and display text
    """
    status_mapping = {
        'Submitted': {
            'color': 'blue',
            'icon': '📝',
            'text': 'Submitted',
            'description': 'Shipment has been submitted and is awaiting admin review'
        },
        'Acknowledged': {
            'color': 'green',
            'icon': '✅',
            'text': 'Acknowledged',
            'description': 'Shipment has been reviewed and acknowledged by admin'
        },
        'Document_Generated': {
            'color': 'purple',
            'icon': '📄',
            'text': 'Documents Generated',
            'description': 'Official documents have been generated for this shipment'
        },
        'Delivered': {
            'color': 'green',
            'icon': '🚚',
            'text': 'Delivered',
            'description': 'Package has been delivered to destination'
        },
        'Failed': {
            'color': 'red',
            'icon': '❌',
            'text': 'Failed',
            'description': 'Shipment processing failed - contact admin'
        },
        'Needs_Changes': {
            'color': 'orange',
            'icon': '⚠️',
            'text': 'Needs Changes',
            'description': 'Shipment requires modifications - check admin comments'
        },
        'Combined': {
            'color': 'purple',
            'icon': '🔄',
            'text': 'Combined',
            'description': 'This package is part of a combined shipment'
        }
    }
    
    return status_mapping.get(status, {
        'color': 'gray',
        'icon': '📦',
        'text': status.replace('_', ' ').title(),
        'description': 'Status information not available'
    })

# Error handlers for tracking blueprint
@tracking.errorhandler(404)
def tracking_not_found(error):
    """Handle 404 errors in tracking blueprint"""
    return render_template('tracking/track_error.html',
                         error_type='not_found',
                         message='The page you are looking for was not found.'), 404

@tracking.errorhandler(500)
def tracking_server_error(error):
    """Handle 500 errors in tracking blueprint"""
    return render_template('tracking/track_error.html',
                         error_type='system_error',
                         message='A system error occurred. Please try again later.'), 500
