"""Empty revision so we can roll back to empty db

Revision ID: 0001
Revises: 
Create Date: 2017-12-26 14:14:00.435012

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
