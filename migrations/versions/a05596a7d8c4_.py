"""empty message

Revision ID: a05596a7d8c4
Revises: 45d6f99b65d1
Create Date: 2023-04-12 17:38:41.081202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a05596a7d8c4'
down_revision = '45d6f99b65d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('query', schema=None) as batch_op:
        batch_op.add_column(sa.Column('task_id', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('query', schema=None) as batch_op:
        batch_op.drop_column('task_id')

    # ### end Alembic commands ###