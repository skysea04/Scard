"""empty message

Revision ID: fce2d02b9669
Revises: b173f0267419
Create Date: 2021-06-19 17:54:19.416367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fce2d02b9669'
down_revision = 'b173f0267419'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('first_img', sa.String(length=255), nullable=True))
    op.add_column('post', sa.Column('comment_count', sa.Integer(), server_default=sa.text('0'), nullable=False))
    op.add_column('user', sa.Column('comment_avatar', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'comment_avatar')
    op.drop_column('post', 'comment_count')
    op.drop_column('post', 'first_img')
    # ### end Alembic commands ###