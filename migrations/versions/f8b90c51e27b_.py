"""empty message

Revision ID: f8b90c51e27b
Revises: b499bd9608a5
Create Date: 2023-04-14 14:47:13.412965

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8b90c51e27b'
down_revision = 'b499bd9608a5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('data_point', schema=None) as batch_op:
        batch_op.add_column(sa.Column('geometry', sa.JSON(), nullable=True))

    with op.batch_alter_table('layer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('primary_parcel_layer', sa.Boolean(), nullable=True))

    with op.batch_alter_table('query', schema=None) as batch_op:
        batch_op.add_column(sa.Column('city', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('county', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('query', schema=None) as batch_op:
        batch_op.drop_column('county')
        batch_op.drop_column('city')

    with op.batch_alter_table('layer', schema=None) as batch_op:
        batch_op.drop_column('primary_parcel_layer')

    with op.batch_alter_table('data_point', schema=None) as batch_op:
        batch_op.drop_column('geometry')

    # ### end Alembic commands ###
