from flask_login import UserMixin
from datetime import datetime, timedelta
import secrets
import string
import pyotp
import hashlib
from . import db

# Association table for many-to-many relationship between users and roles
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """User model for authentication and user management"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    organization = db.Column(db.String(100), nullable=True)
    unique_id = db.Column(db.String(6), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Email verification fields
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100), nullable=True)
    email_verification_expires = db.Column(db.DateTime, nullable=True)
    
    # Two-Factor Authentication fields
    two_fa_enabled = db.Column(db.Boolean, default=False)
    two_fa_secret = db.Column(db.String(32), nullable=True)  # TOTP secret key
    backup_codes = db.Column(db.Text, nullable=True)  # JSON array of backup codes
    
    # Profile picture field
    profile_picture = db.Column(db.String(255), nullable=True)  # Filename of uploaded profile picture
    
    # Enhanced Profile Fields
    # Personal Information
    middle_name = db.Column(db.String(50), nullable=True)
    passport_first_name = db.Column(db.String(50), nullable=True)
    passport_middle_name = db.Column(db.String(50), nullable=True)
    passport_last_name = db.Column(db.String(50), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # Male, Female, Other
    nationality = db.Column(db.String(50), nullable=True)
    t_shirt_size = db.Column(db.String(10), nullable=True)  # XS, S, M, L, XL, XXL, XXXL
    
    # Contact Information
    phone_verified = db.Column(db.Boolean, default=False)
    phone_verification_token = db.Column(db.String(6), nullable=True)
    phone_verification_expires = db.Column(db.DateTime, nullable=True)
    secondary_email = db.Column(db.String(120), nullable=True)
    secondary_email_verified = db.Column(db.Boolean, default=False)
    secondary_email_verification_token = db.Column(db.String(100), nullable=True)
    secondary_email_verification_expires = db.Column(db.DateTime, nullable=True)
    
    # Address Information
    address_line1 = db.Column(db.String(200), nullable=True)
    address_line2 = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state_province = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    
    # Passport Information
    passport_number = db.Column(db.String(50), nullable=True)
    passport_issue_date = db.Column(db.Date, nullable=True)
    passport_expiry_date = db.Column(db.Date, nullable=True)
    passport_front_page = db.Column(db.String(255), nullable=True)  # File path
    passport_last_page = db.Column(db.String(255), nullable=True)   # File path
    
    # Organization Reference
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    
    # Profile completion tracking
    profile_completed = db.Column(db.Boolean, default=False)
    profile_completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    roles = db.relationship('Role', secondary=user_roles, back_populates='users')
    organization_ref = db.relationship('Organization', foreign_keys=[organization_id], backref='members')
    
    @staticmethod
    def generate_unique_id():
        """Generate a unique 6-character alphanumeric ID"""
        while True:
            # Generate a 6-character ID using letters and numbers
            chars = string.ascii_uppercase + string.digits
            unique_id = ''.join(secrets.choice(chars) for _ in range(6))
            
            # Check if this ID already exists
            if not User.query.filter_by(unique_id=unique_id).first():
                return unique_id
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        return any(role.name == role_name for role in self.roles)
    
    def is_admin(self):
        """Check if user is an admin"""
        return self.has_role('Admin')
    
    def is_pi(self):
        """Check if user is a Project Incharge"""
        return self.has_role('Project Incharge')
    
    def is_field_personnel(self):
        """Check if user is Field Personnel"""
        return self.has_role('Field Personnel')
    
    def generate_email_verification_token(self):
        """Generate a secure token for email verification"""
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        self.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
        return token
    
    def verify_email_token(self, token):
        """Verify email verification token"""
        if (self.email_verification_token == token and 
            self.email_verification_expires and 
            datetime.utcnow() < self.email_verification_expires):
            self.email_verified = True
            self.email_verification_token = None
            self.email_verification_expires = None
            return True
        return False
    
    def generate_2fa_secret(self):
        """Generate a new TOTP secret for 2FA"""
        if not self.two_fa_secret:
            self.two_fa_secret = pyotp.random_base32()
        return self.two_fa_secret
    
    def get_2fa_uri(self, app_name='COMPASS-NCPOR'):
        """Get the URI for QR code generation"""
        if self.two_fa_secret:
            return pyotp.totp.TOTP(self.two_fa_secret).provisioning_uri(
                name=self.email,
                issuer_name=app_name
            )
        return None
    
    def verify_2fa_token(self, token):
        """Verify TOTP token"""
        if self.two_fa_secret:
            totp = pyotp.TOTP(self.two_fa_secret)
            return totp.verify(token, valid_window=1)  # Allow 1 step tolerance
        return False
    
    def generate_backup_codes(self, count=10):
        """Generate backup codes for 2FA"""
        import json
        codes = [secrets.token_hex(4).upper() for _ in range(count)]
        self.backup_codes = json.dumps(codes)
        return codes
    
    def verify_backup_code(self, code):
        """Verify and consume a backup code"""
        if not self.backup_codes:
            return False
        
        import json
        try:
            codes = json.loads(self.backup_codes)
            if code.upper() in codes:
                codes.remove(code.upper())
                self.backup_codes = json.dumps(codes)
                return True
        except (json.JSONDecodeError, ValueError):
            pass
        return False
    
    def get_remaining_backup_codes(self):
        """Get count of remaining backup codes"""
        if not self.backup_codes:
            return 0
        
        import json
        try:
            codes = json.loads(self.backup_codes)
            return len(codes)
        except (json.JSONDecodeError, ValueError):
            return 0
    
    def get_profile_picture_url(self):
        """Get the URL for the user's profile picture"""
        if self.profile_picture:
            from flask import request, url_for
            # Use url_for to generate proper URLs that work across network
            return url_for('static', filename=f'uploads/profile_pictures/{self.profile_picture}', _external=True)
        return None
    
    def get_initials(self):
        """Get user initials for avatar fallback"""
        return f"{self.first_name[0] if self.first_name else ''}{self.last_name[0] if self.last_name else ''}".upper()
    
    def get_full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_passport_full_name(self):
        """Get user's full name as per passport"""
        names = [self.passport_first_name, self.passport_middle_name, self.passport_last_name]
        return " ".join(name for name in names if name)
    
    def get_complete_address(self):
        """Get complete formatted address"""
        address_parts = []
        if self.address_line1:
            address_parts.append(self.address_line1)
        if self.address_line2:
            address_parts.append(self.address_line2)
        if self.city:
            address_parts.append(self.city)
        if self.state_province:
            address_parts.append(self.state_province)
        if self.postal_code:
            address_parts.append(self.postal_code)
        if self.country:
            address_parts.append(self.country)
        return ", ".join(address_parts) if address_parts else None
    
    def is_profile_complete(self):
        """Check if user profile is complete"""
        required_fields = [
            self.passport_first_name,
            self.passport_last_name,
            self.date_of_birth,
            self.gender,
            self.nationality,
            self.phone,
            self.address_line1,
            self.city,
            self.country,
            self.passport_number,
            self.passport_issue_date,
            self.passport_expiry_date
        ]
        return all(field is not None and field != '' for field in required_fields)
    
    def get_profile_completion_percentage(self):
        """Get profile completion percentage"""
        total_fields = 20  # Total important fields
        completed_fields = 0
        
        # Basic fields
        if self.passport_first_name: completed_fields += 1
        if self.passport_last_name: completed_fields += 1
        if self.date_of_birth: completed_fields += 1
        if self.gender: completed_fields += 1
        if self.nationality: completed_fields += 1
        if self.phone: completed_fields += 1
        if self.phone_verified: completed_fields += 1
        if self.organization_id: completed_fields += 1
        
        # Address fields
        if self.address_line1: completed_fields += 1
        if self.city: completed_fields += 1
        if self.state_province: completed_fields += 1
        if self.postal_code: completed_fields += 1
        if self.country: completed_fields += 1
        
        # Passport fields
        if self.passport_number: completed_fields += 1
        if self.passport_issue_date: completed_fields += 1
        if self.passport_expiry_date: completed_fields += 1
        if self.passport_front_page: completed_fields += 1
        if self.passport_last_page: completed_fields += 1
        
        # Additional fields
        if self.profile_picture: completed_fields += 1
        if self.t_shirt_size: completed_fields += 1
        
        return int((completed_fields / total_fields) * 100)
    
    def generate_phone_verification_token(self):
        """Generate a phone verification token"""
        if self.phone:
            return PhoneOTP.create_otp(self.phone, 'verification', 15)
        return None
    
    def verify_phone_token(self, token):
        """Verify phone verification token"""
        if self.phone and PhoneOTP.verify_otp(self.phone, token, 'verification'):
            self.phone_verified = True
            db.session.commit()
            return True
        return False
    
    def generate_secondary_email_verification_token(self):
        """Generate a secure token for secondary email verification"""
        token = secrets.token_urlsafe(32)
        self.secondary_email_verification_token = token
        self.secondary_email_verification_expires = datetime.utcnow() + timedelta(hours=24)
        return token
    
    def verify_secondary_email_token(self, token):
        """Verify secondary email verification token"""
        if (self.secondary_email_verification_token == token and 
            self.secondary_email_verification_expires and 
            datetime.utcnow() < self.secondary_email_verification_expires):
            self.secondary_email_verified = True
            self.secondary_email_verification_token = None
            self.secondary_email_verification_expires = None
            return True
        return False
    
    def mark_profile_complete(self):
        """Mark user profile as complete"""
        if self.is_profile_complete():
            self.profile_completed = True
            self.profile_completed_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def __repr__(self):
        return f'<User {self.email}>'

class Role(db.Model):
    """Role model for user permissions"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    # Relationships
    users = db.relationship('User', secondary=user_roles, back_populates='roles')
    
    def __repr__(self):
        return f'<Role {self.name}>'

class EmailOTP(db.Model):
    """Model to store email verification OTPs"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)  # 'registration', 'login', 'password_reset'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    @staticmethod
    def create_otp(email, purpose, expiry_minutes=15):
        """Create a new OTP for email verification"""
        # Invalidate any existing OTPs for this email and purpose
        existing_otps = EmailOTP.query.filter_by(
            email=email, 
            purpose=purpose, 
            is_used=False
        ).all()
        for otp in existing_otps:
            otp.is_used = True
        
        # Create new OTP
        otp_code = EmailOTP.generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        
        new_otp = EmailOTP(
            email=email,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=expires_at
        )
        
        db.session.add(new_otp)
        db.session.commit()
        
        return otp_code
    
    @staticmethod
    def verify_otp(email, otp_code, purpose):
        """Verify OTP code"""
        otp_record = EmailOTP.query.filter_by(
            email=email,
            otp_code=otp_code,
            purpose=purpose,
            is_used=False
        ).first()
        
        if not otp_record:
            return False
        
        # Check if OTP has expired
        if datetime.utcnow() > otp_record.expires_at:
            otp_record.is_used = True
            db.session.commit()
            return False
        
        # Check attempt limit (max 5 attempts)
        otp_record.attempts += 1
        if otp_record.attempts > 5:
            otp_record.is_used = True
            db.session.commit()
            return False
        
        # Mark as used and return success
        otp_record.is_used = True
        db.session.commit()
        return True
    
    def __repr__(self):
        return f'<EmailOTP {self.email} - {self.purpose}>'

class Shipment(db.Model):
    """Shipment model to track shipments created by users"""
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(10), nullable=False)  # 4-digit serial number
    shipment_type = db.Column(db.String(50), nullable=False)  # export, import, reimport, cold
    status = db.Column(db.String(50), default='Submitted')  # Submitted, Acknowledged, Document_Generated, Delivered, Failed, Needs_Changes, Combined
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Comment system
    admin_comment = db.Column(db.Text, nullable=True)  # Admin comments/feedback
    comment_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    comment_at = db.Column(db.DateTime, nullable=True)
    
    # Combined shipment tracking
    is_combined = db.Column(db.Boolean, default=False)
    combined_shipment_id = db.Column(db.String(20), nullable=True)  # Unique combined ID
    parent_shipment_ids = db.Column(db.Text, nullable=True)  # JSON array of original shipment IDs
    
    # Shipment details
    requester_name = db.Column(db.String(100))
    expedition_year = db.Column(db.String(10))
    batch_number = db.Column(db.String(50))
    destination_country = db.Column(db.String(100))
    total_packages = db.Column(db.Integer)
    
    # File reference number (generated when admin acknowledges)
    file_reference_number = db.Column(db.String(100), nullable=True)
    
    # Signing authority for document generation
    signing_authority_id = db.Column(db.Integer, db.ForeignKey('signing_authority.id'), nullable=True)
    
    # Store complete form data as JSON for document generation later
    form_data = db.Column(db.Text)  # JSON string of all form data
    
    # Relationships with explicit foreign_keys to avoid ambiguity
    created_by_user = db.relationship('User', foreign_keys=[created_by], backref='created_shipments')
    acknowledged_by_user = db.relationship('User', foreign_keys=[acknowledged_by], backref='acknowledged_shipments')
    comment_by_user = db.relationship('User', foreign_keys=[comment_by], backref='commented_shipments')
    package_qr_codes = db.relationship('PackageQRCode', backref='shipment', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Shipment {self.invoice_number}>'

class CombinedShipmentCounter(db.Model):
    """Model to track unique combined shipment numbers"""
    id = db.Column(db.Integer, primary_key=True)
    counter = db.Column(db.Integer, default=0, nullable=False)
    
    @classmethod
    def get_next_number(cls):
        """Get the next unique combined shipment number"""
        counter_record = cls.query.first()
        if not counter_record:
            counter_record = cls(counter=1)
            db.session.add(counter_record)
        else:
            counter_record.counter += 1
        
        db.session.commit()
        return counter_record.counter
    
    @classmethod
    def reset_counter(cls):
        """Reset counter based on actual combined shipments in database"""
        from . import db
        # Count actual combined shipments
        actual_count = db.session.query(Shipment).filter(Shipment.is_combined == True).count()
        
        counter_record = cls.query.first()
        if not counter_record:
            counter_record = cls(counter=actual_count)
            db.session.add(counter_record)
        else:
            counter_record.counter = actual_count
        
        db.session.commit()
        return counter_record.counter

class ShipmentSerialCounter(db.Model):
    """Model to track unique shipment serial numbers"""
    id = db.Column(db.Integer, primary_key=True)
    counter = db.Column(db.Integer, default=0, nullable=False)
    
    @classmethod
    def get_next_serial(cls):
        """Get the next unique shipment serial number (4-digit format) with auto-optimization"""
        from . import db
        
        # Auto-optimize counter if needed
        shipment_count = db.session.query(Shipment).count()
        counter_record = cls.query.first()
        
        if not counter_record:
            # Initialize counter based on actual shipments
            counter_record = cls(counter=shipment_count + 1)
            db.session.add(counter_record)
        elif counter_record.counter < shipment_count:
            # Counter is behind - sync it
            counter_record.counter = shipment_count + 1
        else:
            # Normal increment
            counter_record.counter += 1
        
        db.session.commit()
        return f"{counter_record.counter:04d}"  # Returns 4-digit format like 0001, 0002, etc.
    
    @classmethod
    def reset_counter(cls):
        """Reset counter based on actual shipments in database"""
        from . import db
        # Count actual shipments
        actual_count = db.session.query(Shipment).count()
        
        counter_record = cls.query.first()
        if not counter_record:
            counter_record = cls(counter=actual_count)
            db.session.add(counter_record)
        else:
            counter_record.counter = actual_count
        
        db.session.commit()
        return counter_record.counter

class FileReferenceCounter(db.Model):
    """Model to track unique file reference numbers"""
    id = db.Column(db.Integer, primary_key=True)
    counter = db.Column(db.Integer, default=0, nullable=False)
    
    @classmethod
    def get_next_file_reference_serial(cls):
        """Get the next unique file reference serial number (4-digit format)"""
        counter_record = cls.query.first()
        if not counter_record:
            counter_record = cls(counter=1)
            db.session.add(counter_record)
        else:
            counter_record.counter += 1
        
        db.session.commit()
        return f"{counter_record.counter:04d}"  # Returns 4-digit format like 0001, 0002, etc.
    
    @classmethod
    def reset_counter(cls):
        """Reset counter based on actual file references in database"""
        from . import db
        # Count actual shipments with file reference numbers
        actual_count = db.session.query(Shipment).filter(Shipment.file_reference_number.isnot(None)).count()
        
        counter_record = cls.query.first()
        if not counter_record:
            counter_record = cls(counter=actual_count)
            db.session.add(counter_record)
        else:
            counter_record.counter = actual_count
        
        db.session.commit()
        return counter_record.counter

class SigningAuthority(db.Model):
    """Model to store signing authority details for documents"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    organisation = db.Column(db.String(150), nullable=False)
    
    # Hindi fields for bilingual support
    name_hindi = db.Column(db.String(200), nullable=True)
    designation_hindi = db.Column(db.String(200), nullable=True)
    department_hindi = db.Column(db.String(200), nullable=True)
    
    contact_number = db.Column(db.String(20), nullable=True)
    contact_fax = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    created_by_user = db.relationship('User', backref='created_signing_authorities')
    shipments = db.relationship('Shipment', backref='signing_authority')
    
    def __repr__(self):
        return f'<SigningAuthority {self.name} - {self.designation}>'

class TrustedDevice(db.Model):
    """Model to store trusted devices for 2FA bypass"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_fingerprint = db.Column(db.String(64), nullable=False)  # Hashed device identifier
    device_name = db.Column(db.String(100), nullable=True)  # User-friendly device name
    user_agent = db.Column(db.Text, nullable=True)  # Browser/device info
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 or IPv6
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)  # When trust expires
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref='trusted_devices')
    
    @staticmethod
    def generate_device_fingerprint(user_agent, ip_address):
        """Generate a unique fingerprint for a device"""
        # Create a unique identifier based on user agent and IP
        fingerprint_data = f"{user_agent}:{ip_address}:{secrets.token_hex(8)}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    @staticmethod
    def create_trusted_device(user_id, user_agent, ip_address, device_name=None, trust_duration_days=30):
        """Create a new trusted device for a user"""
        device_fingerprint = TrustedDevice.generate_device_fingerprint(user_agent, ip_address)
        expires_at = datetime.utcnow() + timedelta(days=trust_duration_days)
        
        # Check if device already exists and update it
        existing_device = TrustedDevice.query.filter_by(
            user_id=user_id,
            device_fingerprint=device_fingerprint
        ).first()
        
        if existing_device:
            existing_device.last_used_at = datetime.utcnow()
            existing_device.expires_at = expires_at
            existing_device.is_active = True
            existing_device.device_name = device_name or existing_device.device_name
            db.session.commit()
            return existing_device
        
        # Create new trusted device
        trusted_device = TrustedDevice(
            user_id=user_id,
            device_fingerprint=device_fingerprint,
            device_name=device_name or TrustedDevice.get_device_name_from_user_agent(user_agent),
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at
        )
        
        db.session.add(trusted_device)
        db.session.commit()
        return trusted_device
    
    @staticmethod
    def is_device_trusted(user_id, user_agent, ip_address):
        """Check if a device is trusted for a user"""
        device_fingerprint = TrustedDevice.generate_device_fingerprint(user_agent, ip_address)
        
        trusted_device = TrustedDevice.query.filter_by(
            user_id=user_id,
            device_fingerprint=device_fingerprint,
            is_active=True
        ).filter(
            TrustedDevice.expires_at > datetime.utcnow()
        ).first()
        
        if trusted_device:
            # Update last used time
            trusted_device.last_used_at = datetime.utcnow()
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def cleanup_expired_devices():
        """Remove expired trusted devices"""
        expired_devices = TrustedDevice.query.filter(
            TrustedDevice.expires_at < datetime.utcnow()
        ).all()
        
        for device in expired_devices:
            db.session.delete(device)
        
        db.session.commit()
        return len(expired_devices)
    
    @staticmethod
    def get_device_name_from_user_agent(user_agent):
        """Extract a friendly device name from user agent string"""
        if not user_agent:
            return "Unknown Device"
        
        user_agent = user_agent.lower()
        
        # Detect browser
        if 'chrome' in user_agent and 'edge' not in user_agent:
            browser = "Chrome"
        elif 'firefox' in user_agent:
            browser = "Firefox"
        elif 'safari' in user_agent and 'chrome' not in user_agent:
            browser = "Safari"
        elif 'edge' in user_agent:
            browser = "Edge"
        else:
            browser = "Browser"
        
        # Detect OS
        if 'windows' in user_agent:
            os = "Windows"
        elif 'mac' in user_agent:
            os = "Mac"
        elif 'linux' in user_agent:
            os = "Linux"
        elif 'android' in user_agent:
            os = "Android"
        elif 'iphone' in user_agent or 'ipad' in user_agent:
            os = "iOS"
        else:
            os = "Unknown OS"
        
        return f"{browser} on {os}"
    
    def get_time_until_expiry(self):
        """Get human-readable time until device trust expires"""
        if self.expires_at <= datetime.utcnow():
            return "Expired"
        
        delta = self.expires_at - datetime.utcnow()
        days = delta.days
        
        if days > 30:
            return f"{days // 30} month(s)"
        elif days > 0:
            return f"{days} day(s)"
        else:
            hours = delta.seconds // 3600
            return f"{hours} hour(s)"
    
    def revoke(self):
        """Revoke trust for this device"""
        self.is_active = False
        db.session.commit()
    
    def __repr__(self):
        return f'<TrustedDevice {self.device_name} for User {self.user_id}>'

class Organization(db.Model):
    """Model for organizations that users can belong to"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    short_name = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(200), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    country = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def __repr__(self):
        return f'<Organization {self.name}>'

class PackageQRCode(db.Model):
    """Model to track individual package QR codes for shipment tracking"""
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipment.id'), nullable=False)
    package_number = db.Column(db.Integer, nullable=False)  # Package number within the shipment (1, 2, 3, etc.)
    unique_code = db.Column(db.String(12), unique=True, nullable=False)  # Unique tracking code
    qr_code_url = db.Column(db.String(255), nullable=False)  # URL that QR code points to
    qr_image_path = db.Column(db.String(255), nullable=True)  # Path to generated QR code image
    
    # Package details from form data
    package_type = db.Column(db.String(50), nullable=True)  # cardboard_box, plastic_crate, etc.
    package_description = db.Column(db.String(200), nullable=True)  # Description of package contents
    package_weight = db.Column(db.String(20), nullable=True)  # Weight of package
    package_dimensions = db.Column(db.String(100), nullable=True)  # Dimensions of package
    
    # Additional tracking info
    attention_person_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Who this package is for
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attention_person = db.relationship('User', foreign_keys=[attention_person_id], backref='packages_attention')
    
    @staticmethod
    def generate_unique_code():
        """Generate a unique 12-character alphanumeric tracking code"""
        while True:
            # Generate a 12-character code using letters and numbers for better uniqueness
            chars = string.ascii_uppercase + string.digits
            unique_code = ''.join(secrets.choice(chars) for _ in range(12))
            
            # Check if this code already exists
            if not PackageQRCode.query.filter_by(unique_code=unique_code).first():
                return unique_code
    
    def get_tracking_url(self, base_url):
        """Generate the full tracking URL for this package"""
        return f"{base_url}/track/{self.unique_code}"
    
    def get_package_type_display(self):
        """Get human-readable package type"""
        package_type_mapping = {
            'cardboard_box': '📦 Cardboard Box',
            'plastic_crate': '🗃️ Plastic Crate',
            'metal_trunk': '🗳️ Metal Trunk',
            'zarges': '🧳 Zarges',
            'pelican_case': '💼 Pelican Case',
            'other': '📝 Other'
        }
        return package_type_mapping.get(self.package_type, f'📦 {self.package_type.title()}')
    
    def get_package_info(self):
        """Get comprehensive package information for tracking page"""
        return {
            'tracking_code': self.unique_code,
            'package_number': self.package_number,
            'package_type': self.get_package_type_display(),
            'description': self.package_description,
            'weight': self.package_weight,
            'dimensions': self.package_dimensions,
            'attention_person': self.attention_person.get_full_name() if self.attention_person else None,
            'attention_email': self.attention_person.email if self.attention_person else None,
            'created_at': self.created_at,
            'shipment': {
                'invoice_number': self.shipment.invoice_number,
                'type': self.shipment.shipment_type.title(),
                'status': self.shipment.status.replace('_', ' ').title(),
                'created_by': self.shipment.created_by_user.get_full_name(),
                'created_at': self.shipment.created_at,
                'destination': self.shipment.destination_country,
                'expedition_year': self.shipment.expedition_year,
                'acknowledged_by': self.shipment.acknowledged_by_user.get_full_name() if self.shipment.acknowledged_by_user else None,
                'acknowledged_at': self.shipment.acknowledged_at
            }
        }
    
    def __repr__(self):
        return f'<PackageQRCode {self.unique_code} - Shipment {self.shipment_id}>'

class PhoneOTP(db.Model):
    """Model to store phone verification OTPs"""
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)  # 'verification', 'login'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    @staticmethod
    def create_otp(phone_number, purpose, expiry_minutes=15):
        """Create a new OTP for phone verification"""
        # Invalidate any existing OTPs for this phone and purpose
        existing_otps = PhoneOTP.query.filter_by(
            phone_number=phone_number, 
            purpose=purpose, 
            is_used=False
        ).all()
        for otp in existing_otps:
            otp.is_used = True
        
        # Create new OTP
        otp_code = PhoneOTP.generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        
        new_otp = PhoneOTP(
            phone_number=phone_number,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=expires_at
        )
        
        db.session.add(new_otp)
        db.session.commit()
        
        return otp_code
    
    @staticmethod
    def verify_otp(phone_number, otp_code, purpose):
        """Verify OTP code"""
        otp_record = PhoneOTP.query.filter_by(
            phone_number=phone_number,
            otp_code=otp_code,
            purpose=purpose,
            is_used=False
        ).first()
        
        if not otp_record:
            return False
        
        # Check if OTP has expired
        if datetime.utcnow() > otp_record.expires_at:
            otp_record.is_used = True
            db.session.commit()
            return False
        
        # Check attempt limit (max 5 attempts)
        otp_record.attempts += 1
        if otp_record.attempts > 5:
            otp_record.is_used = True
            db.session.commit()
            return False
        
        # Mark as used and return success
        otp_record.is_used = True
        db.session.commit()
        return True