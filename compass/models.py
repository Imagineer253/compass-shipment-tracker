from flask_login import UserMixin
from datetime import datetime
import secrets
import string
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
    
    # Relationships
    roles = db.relationship('Role', secondary=user_roles, back_populates='users')
    
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
    
    # Signing authority for document generation
    signing_authority_id = db.Column(db.Integer, db.ForeignKey('signing_authority.id'), nullable=True)
    
    # Store complete form data as JSON for document generation later
    form_data = db.Column(db.Text)  # JSON string of all form data
    
    # Relationships with explicit foreign_keys to avoid ambiguity
    created_by_user = db.relationship('User', foreign_keys=[created_by], backref='created_shipments')
    acknowledged_by_user = db.relationship('User', foreign_keys=[acknowledged_by], backref='acknowledged_shipments')
    comment_by_user = db.relationship('User', foreign_keys=[comment_by], backref='commented_shipments')
    
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

class ShipmentSerialCounter(db.Model):
    """Model to track unique shipment serial numbers"""
    id = db.Column(db.Integer, primary_key=True)
    counter = db.Column(db.Integer, default=0, nullable=False)
    
    @classmethod
    def get_next_serial(cls):
        """Get the next unique shipment serial number (4-digit format)"""
        counter_record = cls.query.first()
        if not counter_record:
            counter_record = cls(counter=1)
            db.session.add(counter_record)
        else:
            counter_record.counter += 1
        
        db.session.commit()
        return f"{counter_record.counter:04d}"  # Returns 4-digit format like 0001, 0002, etc.

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