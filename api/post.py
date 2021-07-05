from flask import request, jsonify, session
from . import api, ErrorData, Post, PostUserFollow , PostUserLike, db
# import sys, json
# sys.path.append("..")
# from models.model import Post, PostBoard, PostUserFollow, PostUserLike, db

# 獲取文章資訊
@api.route('/post/<int:post_id>', methods=["GET"])
def get_post(post_id):
    try:
        post = db.session.execute('SELECT user.comment_avatar, postboard.sys_name, postboard.show_name, post.user_name, post.title, post.content, post.create_time, post.like_count, post.comment_count\
        FROM ((post INNER JOIN postboard ON post.board_id = postboard.id)\
        INNER JOIN user ON post.user_id = user.id)\
        WHERE post.id = :id', {'id':post_id}).first()
        have_like = False
        is_follow = False
        if "user" in session:
            user_id = session["user"]["id"]
            like = PostUserLike.query.filter_by(user_id=user_id, post_id=post_id).first()
            follow = PostUserFollow.query.filter_by(user_id=user_id, post_id=post_id).first()
            if like:
                have_like = True
            if follow:
                is_follow = True


        data = {
            "avatar": post.comment_avatar,
            "boardSrc": f'/b/{post.sys_name}',
            "boardName": post.show_name,
            "userName": post.user_name,
            "title": post.title,
            "content": post.content,
            "createTime": post.create_time.strftime('%-m月%-d日 %H:%M'),
            "likeCount": post.like_count,
            "commentCount": post.comment_count,
            "like": have_like,
            'follow': is_follow
        }
        return jsonify(data), 200
    except:
        return jsonify(ErrorData.server_error_data), 500

# 使用者更動對特定文章的按讚
@api.route('/post/<int:post_id>/like', methods=["PATCH"])
def patch_post_like(post_id):
    if 'user' in session:
        user_id = session["user"]["id"]
        like = PostUserLike.query.filter_by(user_id=user_id, post_id=post_id).first()
        if like:
            db.session.delete(like)
            post = Post.query.filter_by(id=post_id).first()
            post.like_count -= 1            
        else:
            like = PostUserLike(user_id=user_id, post_id=post_id)
            db.session.add(like)
            post = Post.query.filter_by(id=post_id).first()
            post.like_count += 1
        db.session.commit()
        data = {
            "likeCount": post.like_count
        }
        return jsonify(data), 200
        
    return jsonify(ErrorData.no_sign_data), 403

# 使用者更動對特定文章的追蹤
@api.route('/post/<int:post_id>/follow', methods=["PATCH"])
def patch_post_follow(post_id):
    if 'user' in session:
        user_id = session['user']['id']
        follow = PostUserFollow.query.filter_by(user_id=user_id, post_id=post_id).first()
        if follow:
            db.session.delete(follow)
            # print('remove')
            # 增新訂閱詳細流程（待補）
        else:
            follow = PostUserFollow(user_id=user_id, post_id=post_id, note_id=f'post{post_id}')
            db.session.add(follow)
            # print('append')
            # 取消訂閱詳細流程（待補）
        db.session.commit()
        data = {
            "ok": True
        }
        return jsonify(data), 200

    return jsonify(ErrorData.no_sign_data), 403

# 獲取使用者追蹤中的文章
@api.route('/post/my-follow', methods=['GET'])
def get_myfollow_post():
    if 'user' in session:
        user_id = session['user']['id']
        posts = PostUserFollow.query.filter_by(user_id=user_id).all()
        post_lst = []
        for post in posts:
            post_lst.append(post.post_id)
        data = {
            'posts': post_lst
        }
        return jsonify(data), 200
    return jsonify(ErrorData.no_sign_data), 403