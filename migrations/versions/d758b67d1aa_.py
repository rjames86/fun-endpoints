"""empty message

Revision ID: d758b67d1aa
Revises: 17d30ab48f11
Create Date: 2014-12-22 16:18:56.621250

"""

# revision identifiers, used by Alembic.
revision = 'd758b67d1aa'
down_revision = '17d30ab48f11'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('token', sa.String(length=64), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'token')
    ### end Alembic commands ###
