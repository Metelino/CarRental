"""empty message

Revision ID: 7df367f7784b
Revises: 52ba28d9828d
Create Date: 2022-03-22 21:28:10.086569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7df367f7784b'
down_revision = '52ba28d9828d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cars', sa.Column('model', sa.String(), nullable=True))
    op.create_index(op.f('ix_cars_model'), 'cars', ['model'], unique=False)
    op.drop_index('ix_rentals_total_price', table_name='rentals')
    op.drop_column('rentals', 'total_price')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rentals', sa.Column('total_price', sa.FLOAT(), nullable=True))
    op.create_index('ix_rentals_total_price', 'rentals', ['total_price'], unique=False)
    op.drop_index(op.f('ix_cars_model'), table_name='cars')
    op.drop_column('cars', 'model')
    # ### end Alembic commands ###
