from flask import jsonify, session
from . import api, ErrorData, Post, PostUserLike, Subscribe, db

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
            follow = Subscribe.query.filter_by(channel_id=f'post_{post_id}', user_id=user_id).first()
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
        user_verify = session["user"]["verify_status"]
        if user_verify == 'stranger':
            return jsonify(ErrorData.verify_mail_data), 403

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
@api.route('/post/<post_id>/follow', methods=["PATCH"])
def patch_post_follow(post_id):
    if 'user' in session:
        user_id = session['user']['id']
        user_verify = session["user"]["verify_status"]
        if user_verify == 'stranger':
            return jsonify(ErrorData.verify_mail_data), 403

        is_follow = True
        sub = Subscribe.query.filter_by(channel_id=f'post_{post_id}', user_id=user_id).first()
        if sub:
            db.session.delete(sub)
            is_follow = False
        else:
            sub = Subscribe(channel_id=f'post_{post_id}', user_id=user_id)
            db.session.add(sub)
        db.session.commit()
        data = {
            "ok": True,
            "isFollow": is_follow
        }
        return jsonify(data), 200

    return jsonify(ErrorData.no_sign_data), 403