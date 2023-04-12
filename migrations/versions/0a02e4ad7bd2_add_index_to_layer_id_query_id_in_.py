"""Add index to layer_id, query_id in DataPoint table

Revision ID: 0a02e4ad7bd2
Revises: 0da58e80b822
Create Date: 2023-04-12 12:11:23.168718

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a02e4ad7bd2'
down_revision = '0da58e80b822'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_datapoint_layer_id', 'data_point', ['layer_id'])
    op.create_index('ix_datapoint_query_id', 'data_point', ['query_id'])


def downgrade():
    op.drop_index('ix_datapoint_layer_id', table_name='data_point')
    op.drop_index('ix_datapoint_query_id', table_name='data_point')
