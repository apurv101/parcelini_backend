"""empty message

Revision ID: 570342a310e2
Revises: c739d1c30934
Create Date: 2023-04-09 00:35:31.542679

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '570342a310e2'
down_revision = 'c739d1c30934'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('layer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('layer', schema=None) as batch_op:
        batch_op.drop_column('is_active')

    # ### end Alembic commands ###