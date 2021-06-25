from flask import request, jsonify, session
from . import api, ErrorData
from datetime import datetime
import sys
sys.path.append("..")
from models.model import Comment, CommentUserLike, Post, User, db

@api.route('/comment/<int:post_id>', methods=["POST"])
def post_comment(post_id):
    if "user" in session:
        user_id = session["user"]["id"]
        user_verify = session["user"]["verify"]
        if user_verify == False:
            return jsonify(ErrorData.basic_profile_data), 403
        
        req_data = request.json
        select_name = req_data["name"]
        content = req_data["content"]
        
        # 查看使用者是否有正確選擇回覆名稱
        user = User.view_user(user_id)
        if select_name == 'full':
            user_name = f'{user.collage} {user.department}'
        elif select_name == 'collage':
            user_name = user.collage
        elif select_name == '匿名':
            user_name = '匿名'
        else:
            return jsonify(ErrorData.wrong_name_data), 400
        
        # 查看使用者是否有填寫回覆內容
        if content == '<p><br></p>':
            return jsonify(ErrorData.wrong_content_data), 400

        # 將回應更新到資料庫，增加comment_count，回傳使用者成功資訊
        post = Post.query.filter_by(id=post_id).first()
        post.comment_count += 1
        new_cmt = Comment(post_id=post_id, user_id=user_id, user_name=user_name, floor=post.comment_count, content=content)
        
        db.session.add(new_cmt)
        db.session.commit()
        data = {
            'id': new_cmt.id,
            'avatar': user.comment_avatar,
            'userName': user_name,
            'floor': post.comment_count,
            'createTime': datetime.now().strftime('%-m月%-d日 %H:%M'),
            'likeCount': 0,
            'content': content
        }
        return jsonify(data), 200
        
    return jsonify(ErrorData.no_sign_data), 403

@api.route('/comment/<int:post_id>', methods=["GET"])
def get_comment(post_id):
    try:
        if "user" in session:
            user_id = session["user"]["id"]
            cmts = db.session.execute('SELECT user.comment_avatar, comment.id, comment.user_name, comment.floor, comment.create_time, comment.like_count, comment.content, comment_user_like.user_id\
            FROM ((comment INNER JOIN user ON comment.user_id=user.id)\
            LEFT JOIN comment_user_like ON comment.id=comment_user_like.comment_id AND comment_user_like.user_id = :user_id)\
            WHERE comment.post_id = :post_id', {'user_id': user_id, 'post_id': post_id}).all()
        else:
            cmts = db.session.execute('SELECT user.comment_avatar, comment.id, comment.user_name, comment.floor, comment.create_time, comment.like_count, comment.content\
            FROM comment INNER JOIN user ON comment.user_id=user.id\
            WHERE comment.post_id= :post_id',{'post_id': post_id}).all()
        cmt_lst = []
        for cmt in cmts:
            try:
                like = True if cmt.user_id else False
            except:
                like = False
            cmt_data = {
                'id': cmt.id,
                'avatar': cmt.comment_avatar,
                'userName': cmt.user_name,
                'floor': cmt.floor,
                'createTime': cmt.create_time.strftime('%-m月%-d日 %H:%M'),
                'likeCount': cmt.like_count,
                'content': cmt.content,
                'like': like
            }
            cmt_lst.append(cmt_data)
        
        return jsonify(cmt_lst), 200
    except:
        return jsonify(ErrorData.server_error_data), 500

@api.route('/comment/<int:comment_id>/like', methods=["PATCH"])
def patch_comment_like(comment_id):
    if 'user' in session:
        user_id = session["user"]["id"]
        like = CommentUserLike.query.filter_by(comment_id=comment_id, user_id=user_id).first()
        if like:
            db.session.delete(like)
            cmt = Comment.query.filter_by(id=comment_id).first()
            cmt.like_count -= 1            
        else:
            like = CommentUserLike(comment_id=comment_id, user_id=user_id)
            db.session.add(like)
            cmt = Comment.query.filter_by(id=comment_id).first()
            cmt.like_count += 1
        db.session.commit()
        data = {
            "likeCount": cmt.like_count
        }
        return jsonify(data), 200
        
    return jsonify(ErrorData.no_sign_data), 403