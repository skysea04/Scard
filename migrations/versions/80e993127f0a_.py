"""empty message

Revision ID: 80e993127f0a
Revises: f01ec5458691
Create Date: 2021-07-03 02:17:02.149216

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80e993127f0a'
down_revision = 'f01ec5458691'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('collage_department_ibfk_1', 'collage_department', type_='foreignkey')
    op.create_foreign_key(None, 'collage_department', 'collage', ['collage_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('comment_ibfk_1', 'comment', type_='foreignkey')
    op.drop_constraint('comment_ibfk_2', 'comment', type_='foreignkey')
    op.create_foreign_key(None, 'comment', 'post', ['post_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'comment', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('comment_user_like_ibfk_2', 'comment_user_like', type_='foreignkey')
    op.drop_constraint('comment_user_like_ibfk_1', 'comment_user_like', type_='foreignkey')
    op.create_foreign_key(None, 'comment_user_like', 'comment', ['comment_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'comment_user_like', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('messages_ibfk_1', 'messages', type_='foreignkey')
    op.drop_constraint('messages_ibfk_2', 'messages', type_='foreignkey')
    op.create_foreign_key(None, 'messages', 'scard', ['scard_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'messages', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('post_ibfk_1', 'post', type_='foreignkey')
    op.drop_constraint('post_ibfk_2', 'post', type_='foreignkey')
    op.create_foreign_key(None, 'post', 'postboard', ['board_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'post', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('post_user_like_ibfk_1', 'post_user_like', type_='foreignkey')
    op.drop_constraint('post_user_like_ibfk_2', 'post_user_like', type_='foreignkey')
    op.create_foreign_key(None, 'post_user_like', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'post_user_like', 'post', ['post_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('scard_ibfk_2', 'scard', type_='foreignkey')
    op.drop_constraint('scard_ibfk_1', 'scard', type_='foreignkey')
    op.create_foreign_key(None, 'scard', 'user', ['user_1'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'scard', 'user', ['user_2'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'scard', type_='foreignkey')
    op.drop_constraint(None, 'scard', type_='foreignkey')
    op.create_foreign_key('scard_ibfk_1', 'scard', 'user', ['user_1'], ['id'])
    op.create_foreign_key('scard_ibfk_2', 'scard', 'user', ['user_2'], ['id'])
    op.drop_constraint(None, 'post_user_like', type_='foreignkey')
    op.drop_constraint(None, 'post_user_like', type_='foreignkey')
    op.create_foreign_key('post_user_like_ibfk_2', 'post_user_like', 'user', ['user_id'], ['id'])
    op.create_foreign_key('post_user_like_ibfk_1', 'post_user_like', 'post', ['post_id'], ['id'])
    op.drop_constraint(None, 'post', type_='foreignkey')
    op.drop_constraint(None, 'post', type_='foreignkey')
    op.create_foreign_key('post_ibfk_2', 'post', 'user', ['user_id'], ['id'])
    op.create_foreign_key('post_ibfk_1', 'post', 'postboard', ['board_id'], ['id'])
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.create_foreign_key('messages_ibfk_2', 'messages', 'user', ['user_id'], ['id'])
    op.create_foreign_key('messages_ibfk_1', 'messages', 'scard', ['scard_id'], ['id'])
    op.drop_constraint(None, 'comment_user_like', type_='foreignkey')
    op.drop_constraint(None, 'comment_user_like', type_='foreignkey')
    op.create_foreign_key('comment_user_like_ibfk_1', 'comment_user_like', 'comment', ['comment_id'], ['id'])
    op.create_foreign_key('comment_user_like_ibfk_2', 'comment_user_like', 'user', ['user_id'], ['id'])
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.create_foreign_key('comment_ibfk_2', 'comment', 'user', ['user_id'], ['id'])
    op.create_foreign_key('comment_ibfk_1', 'comment', 'post', ['post_id'], ['id'])
    op.drop_constraint(None, 'collage_department', type_='foreignkey')
    op.create_foreign_key('collage_department_ibfk_1', 'collage_department', 'collage', ['collage_id'], ['id'])
    # ### end Alembic commands ###
