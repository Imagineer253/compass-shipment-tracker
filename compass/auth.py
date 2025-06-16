from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .models import User, Role, db
import random

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

    # Create new user
    new_user = User(
        email=email,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        organization=organization
    )
    
    # Assign ONLY the selected role (clear any existing roles first for safety)
    new_user.roles.clear()  # Safety: ensure no roles exist
    new_user.roles.append(role)  # Add only the selected role

    try:
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        
        # Log in the user immediately after signup
        login_user(new_user)
        return redirect(url_for('main.shipment_type_selection'))
        
    except Exception as e:
        db.session.rollback()
        if 'UNIQUE constraint failed: user_roles' in str(e):
            flash('Error: There was an issue with role assignment. Please try again.', 'danger')
        elif 'UNIQUE constraint failed' in str(e) and 'email' in str(e):
            flash('Email already registered', 'danger')
        else:
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

    login_user(user, remember=remember)
    user.last_login = datetime.utcnow()
    db.session.commit()

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

@auth.route('/register')
def register():
    """Redirect to signup page for backward compatibility"""
    return redirect(url_for('auth.signup_page')) 
