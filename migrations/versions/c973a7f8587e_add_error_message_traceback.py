"""add error message traceback

Revision ID: c973a7f8587e
Revises: 550ed2004f88
Create Date: 2023-01-09 11:53:56.922149

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'c973a7f8587e'
down_revision = '550ed2004f88'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rechunkrun', sa.Column('error_message_traceback', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('rechunkrun', 'error_message_traceback')
    # ### end Alembic commands ###