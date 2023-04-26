"""empty message

Revision ID: 979c5b54e5f0
Revises: 78dec85ef8a1
Create Date: 2023-04-24 12:20:56.255867

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '979c5b54e5f0'
down_revision = '78dec85ef8a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tonic_word', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lesson_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'tonic_lesson', ['lesson_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tonic_word', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('lesson_id')

    # ### end Alembic commands ###