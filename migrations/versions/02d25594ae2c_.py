"""empty message

Revision ID: 02d25594ae2c
Revises: 01e9d8705673
Create Date: 2023-04-24 12:17:28.592160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02d25594ae2c'
down_revision = '01e9d8705673'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tonic_lesson',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tonic_lesson')
    # ### end Alembic commands ###