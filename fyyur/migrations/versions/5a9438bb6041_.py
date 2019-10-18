"""empty message

Revision ID: 5a9438bb6041
Revises: 7cd9d09ce85c
Create Date: 2019-10-17 19:56:17.389690

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a9438bb6041'
down_revision = '7cd9d09ce85c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('id', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shows', 'id')
    # ### end Alembic commands ###