"""empty message

Revision ID: 6fd0fe6cd843
Revises: 06c71ecdb151
Create Date: 2023-04-21 11:37:51.894203

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6fd0fe6cd843'
down_revision = '06c71ecdb151'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tonic_question', schema=None) as batch_op:
        batch_op.add_column(sa.Column('word_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'tonic_word', ['word_id'], ['id'])
        batch_op.drop_column('word')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tonic_question', schema=None) as batch_op:
        batch_op.add_column(sa.Column('word', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('word_id')

    # ### end Alembic commands ###
