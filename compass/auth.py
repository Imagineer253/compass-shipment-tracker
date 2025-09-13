from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .models import User, Role, EmailOTP, TrustedDevice, db
from .email_service import send_otp_email
import random
import logging

auth = Blueprint('auth', __name__)

def initialize_roles():
    """Initialize default roles if they don't exist"""
    roles = ['Admin', 'Project Incharge', 'Field Personnel']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(
                name=role_name,
                description=f'{role_name} role for COMPASS system'
            )
            db.session.add(role)
    db.session.commit()

@auth.route('/')
def landing():
    # Always show the new interactive dashboard, regardless of authentication status
    return render_template('landing_new.html')

@auth.route('/signup-page')
def signup_page():
    """Display the signup form page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.shipment_type_selection'))
    
    # Initialize roles if they don't exist
    initialize_roles()
    
    return render_template('auth/signup.html')

@auth.route('/signup', methods=['POST'])
def signup():
    # Initialize roles first
    initialize_roles()
    
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone = request.form.get('phone')
    organization = request.form.get('organization')
    role_name = request.form.get('role')

    # Basic input validation
    if not all([email, password, confirm_password, first_name, last_name, phone, organization, role_name]):
        flash('All fields are required', 'danger')
        return redirect(url_for('auth.signup_page'))

    if User.query.filter_by(email=email).first():
        flash('Email already registered', 'danger')
        return redirect(url_for('auth.signup_page'))

    if password != confirm_password:
        flash('Passwords do not match', 'danger')
        return redirect(url_for('auth.signup_page'))

    # Get the role
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        flash('Invalid role selected', 'danger')
        return redirect(url_for('auth.signup_page'))

    try:
        # Store user data in session for email verification
        session['pending_user'] = {
            'email': email,
            'password': generate_password_hash(password, method='pbkdf2:sha256'),
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'organization': organization,
            'role_name': role_name
        }
        
        # Generate and send OTP for email verification
        otp_code = EmailOTP.create_otp(email, 'registration', 15)
        
        # Send verification email
        if send_otp_email(email, f"{first_name} {last_name}", otp_code, 'registration'):
            flash('Registration initiated! Please check your email for the verification code.', 'info')
            return redirect(url_for('auth.verify_email'))
        else:
            flash('Failed to send verification email. Please try again.', 'error')
            return redirect(url_for('auth.signup_page'))
            
    except Exception as e:
        logging.error(f"Signup error: {str(e)}")
        flash(f'Registration failed: {str(e)}', 'danger')
        return redirect(url_for('auth.signup_page'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Show login form
        if current_user.is_authenticated:
            return redirect(url_for('main.shipment_type_selection'))
        return render_template('auth/login.html')
    
    # Handle POST request (form submission)
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.', 'danger')
        return redirect(url_for('auth.login'))

    # Check if user has verified email
    if not user.email_verified:
        flash('Please verify your email address before logging in.', 'warning')
        return redirect(url_for('auth.login'))

    # Check if 2FA is enabled
    if user.two_fa_enabled:
        # Check if this device is trusted
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.remote_addr or 'unknown'
        
        if TrustedDevice.is_device_trusted(user.id, user_agent, ip_address):
            # Device is trusted, bypass 2FA
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('Welcome back! Logged in from trusted device.', 'success')
            return redirect(url_for('main.shipment_type_selection'))
        
        # Device not trusted, require 2FA
        session['user_id'] = user.id
        session['awaiting_2fa'] = True
        session['remember_me'] = remember
        session['user_agent'] = user_agent
        session['ip_address'] = ip_address
        
        flash('Please complete two-factor authentication.', 'info')
        return redirect(url_for('two_fa.verify'))
    
    # Normal login (no 2FA)
    login_user(user, remember=remember)
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Check if this is first-time login and profile needs setup
    if not user.profile_completed:
        flash('Welcome to COMPASS! Please complete your profile setup to continue.', 'info')
        return redirect(url_for('profile.setup'))

    return redirect(url_for('main.shipment_type_selection'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.landing'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate a temporary password
            temp_password = ''.join(str(random.randint(0, 9)) for _ in range(8))
            user.password = generate_password_hash(temp_password, method='pbkdf2:sha256')
            db.session.commit()
            
            # In a real application, you would send this via email
            # For now, we'll just show it in a flash message
            flash(f'Your temporary password is: {temp_password}', 'info')
            return redirect(url_for('auth.login'))
        
        # Don't reveal if the email exists or not
        flash('If an account exists with that email, a temporary password will be sent.', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/forgot_password.html')

@auth.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Handle email verification with OTP"""
    if 'pending_user' not in session:
        flash('No pending registration found. Please sign up first.', 'warning')
        return redirect(url_for('auth.signup_page'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        email = session['pending_user']['email']
        
        if not otp_code:
            flash('Please enter the verification code.', 'warning')
            return render_template('auth/verify_otp.html', email=email)
        
        # Verify OTP
        if EmailOTP.verify_otp(email, otp_code, 'registration'):
            try:
                # Get role
                role = Role.query.filter_by(name=session['pending_user']['role_name']).first()
                if not role:
                    flash('Invalid role. Please sign up again.', 'error')
                    session.pop('pending_user', None)
                    return redirect(url_for('auth.signup_page'))
                
                # Create new user
                new_user = User(
                    email=session['pending_user']['email'],
                    password=session['pending_user']['password'],
                    first_name=session['pending_user']['first_name'],
                    last_name=session['pending_user']['last_name'],
                    phone=session['pending_user']['phone'],
                    organization=session['pending_user']['organization'],
                    unique_id=User.generate_unique_id(),
                    email_verified=True  # Mark as verified
                )
                
                # Assign role
                new_user.roles.append(role)
                
                db.session.add(new_user)
                db.session.commit()
                
                # Clear session
                session.pop('pending_user', None)
                
                flash('Email verified successfully! Registration complete.', 'success')
                
                # Log in the user
                login_user(new_user)
                return redirect(url_for('main.shipment_type_selection'))
                
            except Exception as e:
                db.session.rollback()
                logging.error(f"User creation error: {str(e)}")
                flash(f'Registration failed: {str(e)}', 'error')
                return render_template('auth/verify_otp.html', email=email)
        else:
            flash('Invalid or expired verification code. Please try again.', 'error')
            return render_template('auth/verify_otp.html', email=email)
    
    # GET request - show verification form
    return render_template('auth/verify_otp.html', email=session['pending_user']['email'])

@auth.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend email verification OTP"""
    if 'pending_user' not in session:
        flash('No pending registration found.', 'warning')
        return redirect(url_for('auth.signup_page'))
    
    try:
        email = session['pending_user']['email']
        name = f"{session['pending_user']['first_name']} {session['pending_user']['last_name']}"
        
        # Generate new OTP
        otp_code = EmailOTP.create_otp(email, 'registration', 15)
        
        if send_otp_email(email, name, otp_code, 'registration'):
            flash('Verification code resent! Please check your email.', 'info')
        else:
            flash('Failed to resend verification code. Please try again.', 'error')
            
    except Exception as e:
        logging.error(f"Resend verification error: {str(e)}")
        flash('Failed to resend verification code.', 'error')
    
    return redirect(url_for('auth.verify_email'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page with editing capabilities"""
    if request.method == 'POST':
        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                # Validate file type
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    # Generate unique filename
                    import uuid
                    import os
                    filename = f"{current_user.unique_id}_{uuid.uuid4().hex[:8]}.{file.filename.rsplit('.', 1)[1].lower()}"
                    filepath = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pictures', filename)
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    # Remove old profile picture if exists
                    if current_user.profile_picture:
                        old_filepath = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pictures', current_user.profile_picture)
                        if os.path.exists(old_filepath):
                            os.remove(old_filepath)
                    
                    # Save new file
                    file.save(filepath)
                    current_user.profile_picture = filename
                    
                    flash('Profile picture updated successfully!', 'success')
                else:
                    flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', 'error')
        
        # Handle profile information update
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        organization = request.form.get('organization')
        
        if first_name and last_name:
            current_user.first_name = first_name
            current_user.last_name = last_name
            current_user.phone = phone
            current_user.organization = organization
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        else:
            flash('First name and last name are required.', 'error')
        
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')

@auth.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('All password fields are required.', 'error')
        return redirect(url_for('auth.profile'))
    
    from werkzeug.security import check_password_hash, generate_password_hash
    
    if not check_password_hash(current_user.password, current_password):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('auth.profile'))
    
    if len(new_password) < 6:
        flash('New password must be at least 6 characters long.', 'error')
        return redirect(url_for('auth.profile'))
    
    current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
    db.session.commit()
    
    flash('Password changed successfully!', 'success')
    return redirect(url_for('auth.profile'))

@auth.route('/register')
def register():
    """Redirect to signup page for backward compatibility"""
    return redirect(url_for('auth.signup_page')) 
