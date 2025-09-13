"""add_comprehensive_profile_fields

Revision ID: 1bb685565426
Revises: b2768373db56
Create Date: 2025-08-07 06:45:23.518016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1bb685565426'
down_revision = 'b2768373db56'
branch_labels = None
depends_on = None


def upgrade():
    # Create organization table
    op.create_table('organization',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('short_name', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('contact_email', sa.String(length=120), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create phone_otp table
    op.create_table('phone_otp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('otp_code', sa.String(length=6), nullable=False),
        sa.Column('purpose', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add comprehensive profile fields to user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        # Personal Information
        batch_op.add_column(sa.Column('middle_name', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('passport_first_name', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('passport_middle_name', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('passport_last_name', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('date_of_birth', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('gender', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('nationality', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('t_shirt_size', sa.String(length=10), nullable=True))
        
        # Contact Information
        batch_op.add_column(sa.Column('phone_verified', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('phone_verification_token', sa.String(length=6), nullable=True))
        batch_op.add_column(sa.Column('phone_verification_expires', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('secondary_email', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('secondary_email_verified', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('secondary_email_verification_token', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('secondary_email_verification_expires', sa.DateTime(), nullable=True))
        
        # Address Information
        batch_op.add_column(sa.Column('address_line1', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('address_line2', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('city', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('state_province', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('postal_code', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('country', sa.String(length=100), nullable=True))
        
        # Passport Information
        batch_op.add_column(sa.Column('passport_number', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('passport_issue_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('passport_expiry_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('passport_front_page', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('passport_last_page', sa.String(length=255), nullable=True))
        
        # Organization Reference
        batch_op.add_column(sa.Column('organization_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_user_organization', 'organization', ['organization_id'], ['id'])
        
        # Profile completion tracking
        batch_op.add_column(sa.Column('profile_completed', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('profile_completed_at', sa.DateTime(), nullable=True))
    
    # Set default values for existing users
    from sqlalchemy import text
    connection = op.get_bind()
    
    # Set default values for new boolean fields
    connection.execute(text("""
        UPDATE user 
        SET phone_verified = 0,
            secondary_email_verified = 0,
            profile_completed = 0
        WHERE phone_verified IS NULL
    """))


def downgrade():
    # Remove added columns from user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_organization', type_='foreignkey')
        batch_op.drop_column('profile_completed_at')
        batch_op.drop_column('profile_completed')
        batch_op.drop_column('organization_id')
        batch_op.drop_column('passport_last_page')
        batch_op.drop_column('passport_front_page')
        batch_op.drop_column('passport_expiry_date')
        batch_op.drop_column('passport_issue_date')
        batch_op.drop_column('passport_number')
        batch_op.drop_column('country')
        batch_op.drop_column('postal_code')
        batch_op.drop_column('state_province')
        batch_op.drop_column('city')
        batch_op.drop_column('address_line2')
        batch_op.drop_column('address_line1')
        batch_op.drop_column('secondary_email_verification_expires')
        batch_op.drop_column('secondary_email_verification_token')
        batch_op.drop_column('secondary_email_verified')
        batch_op.drop_column('secondary_email')
        batch_op.drop_column('phone_verification_expires')
        batch_op.drop_column('phone_verification_token')
        batch_op.drop_column('phone_verified')
        batch_op.drop_column('t_shirt_size')
        batch_op.drop_column('nationality')
        batch_op.drop_column('gender')
        batch_op.drop_column('date_of_birth')
        batch_op.drop_column('passport_last_name')
        batch_op.drop_column('passport_middle_name')
        batch_op.drop_column('passport_first_name')
        batch_op.drop_column('middle_name')
    
    # Drop tables
    op.drop_table('phone_otp')
    op.drop_table('organization')
