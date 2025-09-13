from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, current_app
from flask_login import login_required, current_user
from .models import User, EmailOTP, TrustedDevice, db
from .email_service import send_otp_email
import pyotp
import qrcode
import io
import base64
import json
import logging
from datetime import datetime

two_fa = Blueprint('two_fa', __name__, url_prefix='/2fa')

@two_fa.route('/setup')
@login_required
def setup():
    """Display 2FA setup page"""
    if current_user.two_fa_enabled:
        flash('Two-factor authentication is already enabled for your account.', 'info')
        return redirect(url_for('two_fa.manage'))
    
    # Generate secret if not exists
    if not current_user.two_fa_secret:
        current_user.generate_2fa_secret()
        db.session.commit()
    
    # Generate QR code
    qr_uri = current_user.get_2fa_uri(current_app.config.get('TWO_FA_APP_NAME', 'COMPASS-NCPOR'))
    
    # Create QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_image = base64.b64encode(buffer.getvalue()).decode()
    
    return render_template('auth/2fa_setup.html', 
                         qr_image=qr_image, 
                         secret=current_user.two_fa_secret,
                         qr_uri=qr_uri)

@two_fa.route('/enable', methods=['POST'])
@login_required
def enable():
    """Enable 2FA after verification"""
    token = request.form.get('token')
    
    if not token:
        flash('Please enter the verification code.', 'warning')
        return redirect(url_for('two_fa.setup'))
    
    # Verify the token
    if current_user.verify_2fa_token(token):
        current_user.two_fa_enabled = True
        
        # Generate backup codes
        backup_codes = current_user.generate_backup_codes()
        
        db.session.commit()
        
        flash('Two-factor authentication has been successfully enabled!', 'success')
        
        # Show backup codes
        return render_template('auth/2fa_backup_codes.html', backup_codes=backup_codes)
    else:
        flash('Invalid verification code. Please try again.', 'error')
        return redirect(url_for('two_fa.setup'))

@two_fa.route('/disable', methods=['POST'])
@login_required
def disable():
    """Disable 2FA"""
    password = request.form.get('password')
    
    if not password:
        flash('Please enter your password to disable 2FA.', 'warning')
        return redirect(url_for('two_fa.manage'))
    
    from werkzeug.security import check_password_hash
    
    if not check_password_hash(current_user.password, password):
        flash('Incorrect password. Please try again.', 'error')
        return redirect(url_for('two_fa.manage'))
    
    # Disable 2FA
    current_user.two_fa_enabled = False
    current_user.two_fa_secret = None
    current_user.backup_codes = None
    
    db.session.commit()
    
    flash('Two-factor authentication has been disabled.', 'warning')
    return redirect(url_for('two_fa.manage'))

@two_fa.route('/manage')
@login_required
def manage():
    """2FA management page"""
    backup_codes_count = current_user.get_remaining_backup_codes() if current_user.two_fa_enabled else 0
    
    return render_template('auth/2fa_manage.html', 
                         backup_codes_count=backup_codes_count)

@two_fa.route('/backup-codes')
@login_required
def backup_codes():
    """Show backup codes"""
    if not current_user.two_fa_enabled:
        flash('Two-factor authentication is not enabled.', 'warning')
        return redirect(url_for('two_fa.manage'))
    
    # Regenerate backup codes
    new_codes = current_user.generate_backup_codes()
    db.session.commit()
    
    flash('New backup codes generated. Please save them securely.', 'info')
    return render_template('auth/2fa_backup_codes.html', backup_codes=new_codes)

@two_fa.route('/verify', methods=['GET', 'POST'])
def verify():
    """2FA verification during login"""
    if 'user_id' not in session or 'awaiting_2fa' not in session:
        flash('Invalid session. Please log in again.', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user or not user.two_fa_enabled:
        flash('Two-factor authentication is not enabled for this account.', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        token = request.form.get('token')
        use_backup_code = request.form.get('use_backup_code') == 'true'
        
        if not token:
            flash('Please enter a verification code.', 'warning')
            return render_template('auth/2fa_verify.html', 
                                 email=user.email,
                                 backup_codes_available=user.get_remaining_backup_codes() > 0)
        
        verified = False
        
        if use_backup_code:
            # Verify backup code
            verified = user.verify_backup_code(token)
            if verified:
                flash('Login successful using backup code.', 'success')
            else:
                flash('Invalid backup code.', 'error')
        else:
            # Verify TOTP token
            verified = user.verify_2fa_token(token)
            if not verified:
                flash('Invalid verification code.', 'error')
        
        if verified:
            # Check if user wants to trust this device
            trust_device = request.form.get('trust_device') == 'on'
            
            # Complete login
            from flask_login import login_user
            login_user(user, remember=session.get('remember_me', False))
            
            # Update last login time
            from datetime import datetime
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Handle device trust
            if trust_device:
                user_agent = session.get('user_agent', request.headers.get('User-Agent', ''))
                ip_address = session.get('ip_address', request.remote_addr or 'unknown')
                
                # Create trusted device
                trusted_device = TrustedDevice.create_trusted_device(
                    user_id=user.id,
                    user_agent=user_agent,
                    ip_address=ip_address,
                    trust_duration_days=current_app.config.get('TRUSTED_DEVICE_DURATION_DAYS', 30)
                )
                
                flash(f'Device "{trusted_device.device_name}" has been added to your trusted devices for 30 days.', 'success')
            
            # Clear 2FA session
            session.pop('user_id', None)
            session.pop('awaiting_2fa', None)
            session.pop('remember_me', None)
            session.pop('user_agent', None)
            session.pop('ip_address', None)
            
            # Check if profile setup is needed after 2FA
            if not user.profile_completed:
                flash('Welcome to COMPASS! Please complete your profile setup to continue.', 'info')
                return redirect(url_for('profile.setup'))
            
            return redirect(url_for('main.shipment_type_selection'))
        else:
            return render_template('auth/2fa_verify.html',
                                 email=user.email,
                                 backup_codes_available=user.get_remaining_backup_codes() > 0)
    
    # GET request - show verification form
    return render_template('auth/2fa_verify.html',
                         email=user.email,
                         backup_codes_available=user.get_remaining_backup_codes() > 0)

@two_fa.route('/verify-email', methods=['POST'])
def verify_email():
    """Send OTP via email for 2FA"""
    if 'user_id' not in session or 'awaiting_2fa' not in session:
        return jsonify({'success': False, 'message': 'Invalid session'})
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})
    
    try:
        # Generate OTP for login
        otp_code = EmailOTP.create_otp(user.email, 'login', 15)
        
        # Send email
        if send_otp_email(user.email, f"{user.first_name} {user.last_name}", otp_code, 'login'):
            return jsonify({'success': True, 'message': 'Verification code sent to your email'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send email'})
            
    except Exception as e:
        logging.error(f"Email 2FA error: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred'})

@two_fa.route('/verify-email-code', methods=['POST'])
def verify_email_code():
    """Verify OTP sent via email"""
    if 'user_id' not in session or 'awaiting_2fa' not in session:
        return jsonify({'success': False, 'message': 'Invalid session'})
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})
    
    otp_code = request.json.get('otp_code')
    if not otp_code:
        return jsonify({'success': False, 'message': 'OTP code required'})
    
    # Verify email OTP
    if EmailOTP.verify_otp(user.email, otp_code, 'login'):
        # Check if user wants to trust this device
        trust_device = request.json.get('trust_device', False)
        
        # Complete login
        from flask_login import login_user
        login_user(user, remember=session.get('remember_me', False))
        
        # Update last login time
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Handle device trust
        if trust_device:
            user_agent = session.get('user_agent', request.headers.get('User-Agent', ''))
            ip_address = session.get('ip_address', request.remote_addr or 'unknown')
            
            # Create trusted device
            trusted_device = TrustedDevice.create_trusted_device(
                user_id=user.id,
                user_agent=user_agent,
                ip_address=ip_address,
                trust_duration_days=current_app.config.get('TRUSTED_DEVICE_DURATION_DAYS', 30)
            )
        
        # Clear 2FA session
        session.pop('user_id', None)
        session.pop('awaiting_2fa', None)
        session.pop('remember_me', None)
        session.pop('user_agent', None)
        session.pop('ip_address', None)
        
        # Check if profile setup is needed after email verification
        if not user.profile_completed:
            return jsonify({'success': True, 'redirect': url_for('profile.setup')})
        
        return jsonify({'success': True, 'redirect': url_for('main.shipment_type_selection')})
    else:
        return jsonify({'success': False, 'message': 'Invalid or expired OTP code'})

@two_fa.route('/trusted-devices')
@login_required
def trusted_devices():
    """View and manage trusted devices"""
    # Clean up expired devices first
    TrustedDevice.cleanup_expired_devices()
    
    # Get user's trusted devices
    devices = TrustedDevice.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).filter(
        TrustedDevice.expires_at > datetime.utcnow()
    ).order_by(
        TrustedDevice.last_used_at.desc()
    ).all()
    
    return render_template('auth/trusted_devices.html', devices=devices)

@two_fa.route('/revoke-device/<int:device_id>', methods=['POST'])
@login_required
def revoke_device(device_id):
    """Revoke trust for a specific device"""
    device = TrustedDevice.query.filter_by(
        id=device_id,
        user_id=current_user.id
    ).first()
    
    if not device:
        flash('Device not found.', 'error')
        return redirect(url_for('two_fa.trusted_devices'))
    
    device.revoke()
    flash(f'Trust revoked for device "{device.device_name}".', 'success')
    return redirect(url_for('two_fa.trusted_devices'))

@two_fa.route('/revoke-all-devices', methods=['POST'])
@login_required
def revoke_all_devices():
    """Revoke trust for all devices"""
    devices = TrustedDevice.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    count = 0
    for device in devices:
        device.revoke()
        count += 1
    
    flash(f'Trust revoked for {count} device(s).', 'success')
    return redirect(url_for('two_fa.trusted_devices'))
