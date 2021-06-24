from flask import request, jsonify, session
from . import api
import sys
sys.path.append("..")
from models.model import Post, PostBoard, db

@api.route('/post/<int:post_id>', methods=["GET"])
def get_post(post_id):
    post = db.session.execute('SELECT user.comment_avatar, postboard.sys_name, postboard.show_name, post.user_name, post.title, post.content, post.create_time, post.like_count, post.comment_count\
    FROM ((post INNER JOIN postboard ON post.board_id = postboard.id)\
    INNER JOIN user ON post.user_id = user.id)\
    WHERE post.id = :id', {'id':post_id}).first()
    data = {
        "avatar": post.comment_avatar,
        "boardSrc": f'/b/{post.sys_name}',
        "boardName": post.show_name,
        "userName": post.user_name,
        "title": post.title,
        "content": post.content,
        "createTime": post.create_time.strftime('%-m月%-d日 %H:%M'),
        "likeCount": post.like_count,
        "commentCount": post.comment_count
    }
    return jsonify(data), 200