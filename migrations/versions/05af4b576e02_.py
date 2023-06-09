"""empty message

Revision ID: 05af4b576e02
Revises: e073a475ddb2
Create Date: 2023-04-12 12:55:00.886400

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05af4b576e02'
down_revision = 'e073a475ddb2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('data_point', schema=None) as batch_op:
        batch_op.add_column(sa.Column('query_id', sa.String(length=36), nullable=False))
        batch_op.create_foreign_key(None, 'query', ['query_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('data_point', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('query_id')

    # ### end Alembic commands ###
