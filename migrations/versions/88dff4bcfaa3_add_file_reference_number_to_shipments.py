"""add_file_reference_number_to_shipments

Revision ID: 88dff4bcfaa3
Revises: 886326e13fe2
Create Date: 2025-06-21 17:54:09.879659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88dff4bcfaa3'
down_revision = '886326e13fe2'
branch_labels = None
depends_on = None


def upgrade():
    # Add file_reference_number field to shipment table
    op.add_column('shipment', sa.Column('file_reference_number', sa.String(100), nullable=True))


def downgrade():
    # Remove file_reference_number field from shipment table
    op.drop_column('shipment', 'file_reference_number')
