"""empty message

Revision ID: 7cc8af14925f
Revises: f8b90c51e27b
Create Date: 2023-04-16 10:52:29.823167

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cc8af14925f'
down_revision = 'f8b90c51e27b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('layer', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['url'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('layer', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###
