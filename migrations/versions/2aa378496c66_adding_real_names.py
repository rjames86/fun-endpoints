"""adding real names

Revision ID: 2aa378496c66
Revises: a26199ed7a1
Create Date: 2015-03-09 23:56:26.727257

"""

# revision identifiers, used by Alembic.
revision = '2aa378496c66'
down_revision = 'a26199ed7a1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('name', sa.String(length=64), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'name')
    ### end Alembic commands ###
