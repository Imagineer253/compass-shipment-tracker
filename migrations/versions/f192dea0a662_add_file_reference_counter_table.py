"""add_file_reference_counter_table

Revision ID: f192dea0a662
Revises: 88dff4bcfaa3
Create Date: 2025-06-21 17:55:12.683515

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f192dea0a662'
down_revision = '88dff4bcfaa3'
branch_labels = None
depends_on = None


def upgrade():
    # Create file_reference_counter table
    op.create_table('file_reference_counter',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('counter', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop file_reference_counter table
    op.drop_table('file_reference_counter')
