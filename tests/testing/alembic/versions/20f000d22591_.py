"""empty message

Revision ID: 20f000d22591
Revises: 
Create Date: 2022-08-18 15:23:31.257119

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20f000d22591'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade() -> None:
    op.drop_table("user")
