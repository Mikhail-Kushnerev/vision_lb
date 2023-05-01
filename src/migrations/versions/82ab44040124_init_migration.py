"""init_migration

Revision ID: 82ab44040124
Revises: 6c3091b13b83
Create Date: 2023-04-29 21:18:36.505997

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '82ab44040124'
down_revision = '6c3091b13b83'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pointsmodel',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('track_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('points_X', sa.Float(), nullable=True),
    sa.Column('points_Y', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pointsmodel')
    # ### end Alembic commands ###
