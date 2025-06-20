"""Add unique_id field to users

Revision ID: 2c9791241c6b
Revises: dc9a2244290f
Create Date: 2025-06-20 10:52:06.740836

"""
from alembic import op
import sqlalchemy as sa
import secrets
import string
from sqlalchemy.orm import Session
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '2c9791241c6b'
down_revision = 'dc9a2244290f'
branch_labels = None
depends_on = None


def generate_unique_id(session):
    """Generate a unique 6-character alphanumeric ID"""
    while True:
        # Generate a 6-character ID using letters and numbers
        chars = string.ascii_uppercase + string.digits
        unique_id = ''.join(secrets.choice(chars) for _ in range(6))
        
        # Check if this ID already exists in the database
        result = session.execute(text("SELECT COUNT(*) FROM user WHERE unique_id = :unique_id"), {'unique_id': unique_id})
        if result.scalar() == 0:
            return unique_id


def upgrade():
    # Add the unique_id column as nullable first
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('unique_id', sa.String(length=6), nullable=True))

    # Get database connection and session
    bind = op.get_bind()
    session = Session(bind=bind)
    
    try:
        # Get all existing users
        result = session.execute(text("SELECT id FROM user"))
        user_ids = [row[0] for row in result.fetchall()]
        
        # Generate unique IDs for existing users
        for user_id in user_ids:
            unique_id = generate_unique_id(session)
            session.execute(
                text("UPDATE user SET unique_id = :unique_id WHERE id = :user_id"),
                {'unique_id': unique_id, 'user_id': user_id}
            )
        
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    
    # Now make the column non-nullable and add unique constraint
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('unique_id', nullable=False)
        batch_op.create_unique_constraint('uq_user_unique_id', ['unique_id'])


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('uq_user_unique_id', type_='unique')
        batch_op.drop_column('unique_id')
