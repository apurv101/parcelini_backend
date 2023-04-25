"""create indices

Revision ID: 87800a148071
Revises: bcee59eb259e
Create Date: 2023-04-25 17:56:06.924926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87800a148071'
down_revision = 'bcee59eb259e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_tonicword_lesson_id', 'tonic_word', ['lesson_id'])
    op.create_index('ix_tonicquestion_word_id', 'tonic_question', ['word_id'])


def downgrade():
    op.drop_index('ix_tonicword_lesson_id', table_name='tonic_word')
    op.drop_index('ix_tonicquestion_word_id', table_name='tonic_question')
