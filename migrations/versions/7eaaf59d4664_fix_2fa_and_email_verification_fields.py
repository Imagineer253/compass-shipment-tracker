"""Fix 2FA and email verification fields

Revision ID: 7eaaf59d4664
Revises: cfa1e56ddef1
Create Date: 2025-08-06 23:39:47.330626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7eaaf59d4664'
down_revision = 'cfa1e56ddef1'
branch_labels = None
depends_on = None


def upgrade():
    # Add email verification fields to user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_verified', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('email_verification_token', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('email_verification_expires', sa.DateTime(), nullable=True))
        
        # Add 2FA fields to user table
        batch_op.add_column(sa.Column('two_fa_enabled', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('two_fa_secret', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('backup_codes', sa.Text(), nullable=True))
    
    # Create email_otp table
    op.create_table('email_otp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('otp_code', sa.String(length=6), nullable=False),
        sa.Column('purpose', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Set default values for existing users
    from sqlalchemy import text
    connection = op.get_bind()
    
    # Set email_verified to True for existing users (they're already in the system)
    # Set two_fa_enabled to False for existing users
    connection.execute(text("""
        UPDATE user 
        SET email_verified = 1, 
            two_fa_enabled = 0 
        WHERE email_verified IS NULL
    """))


def downgrade():
    # Remove email verification fields from user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('backup_codes')
        batch_op.drop_column('two_fa_secret')
        batch_op.drop_column('two_fa_enabled')
        batch_op.drop_column('email_verification_expires')
        batch_op.drop_column('email_verification_token')
        batch_op.drop_column('email_verified')
    
    # Drop email_otp table
    op.drop_table('email_otp')
