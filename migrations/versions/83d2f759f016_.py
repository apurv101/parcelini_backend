"""empty message

Revision ID: 83d2f759f016
Revises: 49372afba8d6
Create Date: 2023-04-26 16:28:52.149040

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83d2f759f016'
down_revision = '49372afba8d6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tonic_lesson_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('lesson_id', sa.Integer(), nullable=False),
    sa.Column('correct_answered', sa.Integer(), nullable=True),
    sa.Column('incorrect_answered', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lesson_id'], ['tonic_lesson.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['tonic_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('tonic_lesson', schema=None) as batch_op:
        batch_op.add_column(sa.Column('num_question', sa.Integer(), nullable=True))

    with op.batch_alter_table('tonic_user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tonic_user', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    with op.batch_alter_table('tonic_lesson', schema=None) as batch_op:
        batch_op.drop_column('num_question')

    op.drop_table('tonic_lesson_stats')
    # ### end Alembic commands ###