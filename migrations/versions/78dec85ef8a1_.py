"""empty message

Revision ID: 78dec85ef8a1
Revises: 02d25594ae2c
Create Date: 2023-04-24 12:18:38.078453

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78dec85ef8a1'
down_revision = '02d25594ae2c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tonic_score',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('answered_correct', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['tonic_question.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['tonic_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tonic_score')
    # ### end Alembic commands ###
