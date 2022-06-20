"""Change

Revision ID: 5c1a2daff9ce
Revises: 
Create Date: 2022-06-20 15:36:32.978603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c1a2daff9ce'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('change', sa.Column('incident_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'change', 'incident', ['incident_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'change', type_='foreignkey')
    op.drop_column('change', 'incident_id')
    # ### end Alembic commands ###