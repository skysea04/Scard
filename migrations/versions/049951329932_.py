"""empty message

Revision ID: 049951329932
Revises: 8e0bb6a58548
Create Date: 2021-07-03 23:38:57.927518

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '049951329932'
down_revision = '8e0bb6a58548'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('post_user_follow',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('user_post_index', 'post_user_follow', ['user_id', 'post_id'], unique=False)
    op.drop_column('post', 'followers')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('followers', mysql.JSON(), server_default=sa.text('(json_array())'), nullable=True))
    op.drop_index('user_post_index', table_name='post_user_follow')
    op.drop_table('post_user_follow')
    # ### end Alembic commands ###
