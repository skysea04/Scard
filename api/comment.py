from flask import request, jsonify, session
from . import api, ErrorData
import sys
sys.path.append("..")
from models.model import Comment, Post, User, db

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
        new_comment = Comment(post_id=post_id, user_id=user_id, user_name=user_name, floor=post.comment_count, content=content)

        db.session.add(new_comment)
        db.session.commit()
        data = {
            'ok': True
        }
        return jsonify(data), 200
        
    return jsonify(ErrorData.no_sign_data), 403