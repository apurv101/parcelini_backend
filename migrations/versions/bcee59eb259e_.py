"""empty message

Revision ID: bcee59eb259e
Revises: 1b1395cc8467
Create Date: 2023-04-24 17:46:10.223417

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcee59eb259e'
down_revision = '1b1395cc8467'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tonic_question', schema=None) as batch_op:
        batch_op.add_column(sa.Column('question_text', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('option1', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('option2', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('option3', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('option4', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('correct_answer', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tonic_question', schema=None) as batch_op:
        batch_op.drop_column('correct_answer')
        batch_op.drop_column('option4')
        batch_op.drop_column('option3')
        batch_op.drop_column('option2')
        batch_op.drop_column('option1')
        batch_op.drop_column('question_text')

    # ### end Alembic commands ###