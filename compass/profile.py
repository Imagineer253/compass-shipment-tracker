from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date
import os
import uuid
from .models import User, Organization, PhoneOTP, EmailOTP, db
from .email_service import send_otp_email

profile = Blueprint('profile', __name__, url_prefix='/profile')

# Constants for validation
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

COUNTRIES = [
    'Afghanistan', 'Albania', 'Algeria', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Bangladesh',
    'Belgium', 'Bhutan', 'Brazil', 'Bulgaria', 'Canada', 'Chile', 'China', 'Colombia', 'Croatia',
    'Czech Republic', 'Denmark', 'Egypt', 'Finland', 'France', 'Germany', 'Greece', 'Hungary',
    'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Japan',
    'Kazakhstan', 'Kenya', 'Kuwait', 'Malaysia', 'Mexico', 'Nepal', 'Netherlands', 'New Zealand',
    'Norway', 'Pakistan', 'Philippines', 'Poland', 'Portugal', 'Romania', 'Russia', 'Saudi Arabia',
    'Singapore', 'South Africa', 'South Korea', 'Spain', 'Sri Lanka', 'Sweden', 'Switzerland',
    'Thailand', 'Turkey', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States',
    'Vietnam', 'Other'
]

GENDERS = ['Male', 'Female', 'Other']
T_SHIRT_SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, upload_folder, prefix=''):
    """Save uploaded file and return filename"""
    if file and file.filename != '':
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{prefix}{current_user.unique_id}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Ensure upload directory exists
        full_upload_path = os.path.join(current_app.root_path, 'static', 'uploads', upload_folder)
        os.makedirs(full_upload_path, exist_ok=True)
        
        # Save file
        filepath = os.path.join(full_upload_path, unique_filename)
        file.save(filepath)
        
        return unique_filename
    return None

@profile.route('/setup')
@login_required
def setup():
    """Initial profile setup page for new users"""
    if current_user.profile_completed:
        flash('Your profile is already complete.', 'info')
        return redirect(url_for('profile.view'))
    
    # Get organizations for dropdown
    organizations = Organization.query.filter_by(is_active=True).order_by(Organization.name).all()
    
    return render_template('profile/setup.html', 
                         organizations=organizations,
                         countries=COUNTRIES,
                         genders=GENDERS,
                         t_shirt_sizes=T_SHIRT_SIZES)

@profile.route('/setup', methods=['POST'])
@login_required
def setup_post():
    """Handle profile setup form submission"""
    try:
        # Personal Information
        current_user.passport_first_name = request.form.get('passport_first_name', '').strip()
        current_user.passport_middle_name = request.form.get('passport_middle_name', '').strip()
        current_user.passport_last_name = request.form.get('passport_last_name', '').strip()
        
        # Parse date of birth
        dob_str = request.form.get('date_of_birth')
        if dob_str:
            current_user.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
        
        current_user.gender = request.form.get('gender')
        current_user.nationality = request.form.get('nationality')
        current_user.t_shirt_size = request.form.get('t_shirt_size')
        
        # Contact Information
        phone = request.form.get('phone', '').strip()
        if phone != current_user.phone:
            current_user.phone = phone
            current_user.phone_verified = False  # Reset verification if phone changed
        
        secondary_email = request.form.get('secondary_email', '').strip()
        if secondary_email != current_user.secondary_email:
            current_user.secondary_email = secondary_email
            current_user.secondary_email_verified = False  # Reset verification if email changed
        
        # Organization
        org_id = request.form.get('organization_id')
        if org_id:
            current_user.organization_id = int(org_id)
        
        # Address Information
        current_user.address_line1 = request.form.get('address_line1', '').strip()
        current_user.address_line2 = request.form.get('address_line2', '').strip()
        current_user.city = request.form.get('city', '').strip()
        current_user.state_province = request.form.get('state_province', '').strip()
        current_user.postal_code = request.form.get('postal_code', '').strip()
        current_user.country = request.form.get('country')
        
        # Passport Information
        current_user.passport_number = request.form.get('passport_number', '').strip()
        
        # Parse passport dates
        issue_date_str = request.form.get('passport_issue_date')
        if issue_date_str:
            current_user.passport_issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        
        expiry_date_str = request.form.get('passport_expiry_date')
        if expiry_date_str:
            current_user.passport_expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        
        # Handle file uploads
        # Profile picture
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                # Remove old profile picture
                if current_user.profile_picture:
                    old_path = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pictures', current_user.profile_picture)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = save_uploaded_file(file, 'profile_pictures', 'profile_')
                if filename:
                    current_user.profile_picture = filename
        
        # Passport front page
        if 'passport_front_page' in request.files:
            file = request.files['passport_front_page']
            if file and allowed_file(file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
                # Remove old file
                if current_user.passport_front_page:
                    old_path = os.path.join(current_app.root_path, 'static', 'uploads', 'passports', current_user.passport_front_page)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = save_uploaded_file(file, 'passports', 'front_')
                if filename:
                    current_user.passport_front_page = filename
        
        # Passport last page
        if 'passport_last_page' in request.files:
            file = request.files['passport_last_page']
            if file and allowed_file(file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
                # Remove old file
                if current_user.passport_last_page:
                    old_path = os.path.join(current_app.root_path, 'static', 'uploads', 'passports', current_user.passport_last_page)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = save_uploaded_file(file, 'passports', 'last_')
                if filename:
                    current_user.passport_last_page = filename
        
        # Check if profile is now complete
        if current_user.is_profile_complete():
            current_user.mark_profile_complete()
            flash('Profile setup completed successfully! Welcome to COMPASS.', 'success')
        else:
            flash('Profile updated! Please complete all required fields to fully activate your account.', 'info')
        
        db.session.commit()
        
        return redirect(url_for('profile.view'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while saving your profile: {str(e)}', 'error')
        return redirect(url_for('profile.setup'))

@profile.route('/view')
@login_required
def view():
    """View user profile"""
    completion_percentage = current_user.get_profile_completion_percentage()
    return render_template('profile/view.html', completion_percentage=completion_percentage)

@profile.route('/edit')
@login_required
def edit():
    """Edit user profile"""
    organizations = Organization.query.filter_by(is_active=True).order_by(Organization.name).all()
    return render_template('profile/edit.html', 
                         organizations=organizations,
                         countries=COUNTRIES,
                         genders=GENDERS,
                         t_shirt_sizes=T_SHIRT_SIZES)

@profile.route('/edit', methods=['POST'])
@login_required
def edit_post():
    """Handle profile edit form submission"""
    # Reuse the same logic as setup_post
    return setup_post()

@profile.route('/verify-phone', methods=['POST'])
@login_required
def verify_phone():
    """Send OTP to phone for verification"""
    if not current_user.phone:
        return jsonify({'success': False, 'message': 'No phone number provided'})
    
    try:
        # Generate OTP for phone verification
        otp_code = PhoneOTP.create_otp(current_user.phone, 'verification', 15)
        
        # Here you would integrate with SMS service (Twilio, AWS SNS, etc.)
        # For now, we'll just log it
        print(f"SMS OTP for {current_user.phone}: {otp_code}")
        
        # In production, replace with actual SMS sending
        flash(f'Verification code sent to {current_user.phone}. Code: {otp_code} (Development mode)', 'info')
        
        return jsonify({'success': True, 'message': f'Verification code sent to {current_user.phone}'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to send verification code: {str(e)}'})

@profile.route('/verify-phone-code', methods=['POST'])
@login_required
def verify_phone_code():
    """Verify phone OTP code"""
    otp_code = request.json.get('otp_code')
    
    if not otp_code:
        return jsonify({'success': False, 'message': 'OTP code required'})
    
    if PhoneOTP.verify_otp(current_user.phone, otp_code, 'verification'):
        current_user.phone_verified = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Phone number verified successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Invalid or expired OTP code'})

@profile.route('/verify-secondary-email', methods=['POST'])
@login_required
def verify_secondary_email():
    """Send verification email to secondary email"""
    if not current_user.secondary_email:
        return jsonify({'success': False, 'message': 'No secondary email provided'})
    
    try:
        # Generate verification token
        token = current_user.generate_secondary_email_verification_token()
        db.session.commit()
        
        # Send verification email
        if send_otp_email(current_user.secondary_email, current_user.get_full_name(), token[:6], 'registration'):
            return jsonify({'success': True, 'message': f'Verification email sent to {current_user.secondary_email}'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send verification email'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to send verification email: {str(e)}'})

@profile.route('/verify-secondary-email-code', methods=['POST'])
@login_required
def verify_secondary_email_code():
    """Verify secondary email with token"""
    token = request.json.get('token')
    
    if not token:
        return jsonify({'success': False, 'message': 'Verification token required'})
    
    if current_user.verify_secondary_email_token(token):
        db.session.commit()
        return jsonify({'success': True, 'message': 'Secondary email verified successfully!'})
    else:
        return jsonify({'success': False, 'message': 'Invalid or expired verification token'})

@profile.route('/check-completion')
@login_required
def check_completion():
    """Check profile completion status"""
    return jsonify({
        'completed': current_user.profile_completed,
        'percentage': current_user.get_profile_completion_percentage(),
        'is_complete': current_user.is_profile_complete()
    })
