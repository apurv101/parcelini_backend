"""empty message

Revision ID: 7c53d425be57
Revises: aa24d7b7795e
Create Date: 2023-04-26 16:56:17.390573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c53d425be57'
down_revision = 'aa24d7b7795e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tonic_lesson_stats', schema=None) as batch_op:
        batch_op.create_unique_constraint('uix_user_lesson', ['user_id', 'lesson_id'])

    with op.batch_alter_table('tonic_score', schema=None) as batch_op:
        batch_op.create_unique_constraint('uix_user_question', ['user_id', 'question_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tonic_score', schema=None) as batch_op:
        batch_op.drop_constraint('uix_user_question', type_='unique')

    with op.batch_alter_table('tonic_lesson_stats', schema=None) as batch_op:
        batch_op.drop_constraint('uix_user_lesson', type_='unique')

    # ### end Alembic commands ###