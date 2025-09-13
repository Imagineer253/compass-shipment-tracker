"""Add profile picture field to users

Revision ID: 25ec23d46ef1
Revises: 7eaaf59d4664
Create Date: 2025-08-07 05:28:58.779321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25ec23d46ef1'
down_revision = '7eaaf59d4664'
branch_labels = None
depends_on = None


def upgrade():
    # Add profile picture field to user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_picture', sa.String(length=255), nullable=True))


def downgrade():
    # Remove profile picture field from user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('profile_picture')
