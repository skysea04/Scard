from flask import request, jsonify, session
from . import api, ErrorData, Comment, CommentUserLike,  Post, PostBoard, User, Subscribe, db
from datetime import datetime
import sys, json
sys.path.append("..")
from app import r
@api.route('/comment/<int:post_id>', methods=["POST"])
def post_comment(post_id):
    if "user" in session:
        user_id = session["user"]["id"]
        user_verify = session["user"]["verify_status"]
        if user_verify == 'stranger':
            return jsonify(ErrorData.verify_mail_data), 403
        elif user_verify == 'mail':
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

        # 將回應更新到資料庫，增加comment_count
        post = Post.query.filter_by(id=post_id).first()
        # board = PostBoard.view_board(post.board_id)
        post.comment_count += 1
        new_cmt = Comment(post_id=post_id, user_id=user_id, user_name=user_name, floor=post.comment_count, content=content)
        db.session.add(new_cmt)

        post_chan = f'post_{post_id}'
        poster_chan = f'post_{post_id}_poster'
        add_follow = False
        if post.user_id != user_id:
            # 幫留言者自動追蹤文章
            user_sub = Subscribe.query.filter_by(channel_id = post_chan, user_id=user_id).first()
            if not user_sub:
                user_sub = Subscribe(channel_id = post_chan, user_id=user_id)
                db.session.add(user_sub)
                add_follow = True



        ## 存通知內容到每個文章訂閱者與原po的redis中
        # 給訂閱者
        note_to_suber = {
            'channel': post_chan,
            'user_id': user_id,
            'msg': f'你追蹤的文章<b>「{post.title}」</b>有新的回應。',
            'href': f'/b/{post.board_id}/p/{post_id}',
            'time': datetime.now().strftime("%-m月%-d日 %H:%M")
        }        
        subers = Subscribe.query.filter_by(channel_id = post_chan).all()
        for suber in subers:
            if suber.user_id == user_id: # 當訂閱者就是發留言者時跳過
                continue
            r.hset(f'user_{suber.user_id}_note', post_chan, json.dumps(note_to_suber))

        # 給原po
        note_to_poster = {
            'channel': poster_chan,
            'user_id': user_id,
            'msg': f'你的文章<b>「{post.title}」</b>有新的回應。',
            'href': f'/b/{post.board_id}/p/{post_id}',
            'time': datetime.now().strftime("%-m月%-d日 %H:%M")
        }
        r.hset(f'user_{post.user_id}_note', poster_chan, json.dumps(note_to_poster))
        
        # pub to channel => 即時通知
        r.publish(post_chan, json.dumps(note_to_suber))
        r.publish(poster_chan, json.dumps(note_to_poster))

        # 確認改動存入資料庫
        db.session.commit()
        data = {
            'id': new_cmt.id,
            'avatar': user.comment_avatar,
            'userName': user_name,
            'floor': post.comment_count,
            'createTime': datetime.now().strftime('%-m月%-d日 %H:%M'),
            'likeCount': 0,
            'content': content,
            'addFollow': add_follow,
            'isAuthor': True
        }
        return jsonify(data), 200
        
    return jsonify(ErrorData.no_sign_data), 403

@api.route('/comment/<int:post_id>', methods=["GET"])
def get_comment(post_id):
    # try:
        cmt_lst = []
        if "user" in session:
            user_id = session["user"]["id"]
            cmts = db.session.execute('SELECT user.comment_avatar, comment.id, comment.user_id as author_id, comment.user_name, comment.floor, comment.create_time, comment.like_count, comment.content, comment.delete, comment_user_like.user_id\
            FROM ((comment INNER JOIN user ON comment.user_id=user.id)\
            LEFT JOIN comment_user_like ON comment.id=comment_user_like.comment_id AND comment_user_like.user_id = :user_id)\
            WHERE comment.post_id = :post_id', {'user_id': user_id, 'post_id': post_id}).all()
            for cmt in cmts:
                like = True if cmt.user_id else False
                is_author = True if cmt.author_id == user_id else False
                cmt_data = {
                    'id': cmt.id,
                    'avatar': cmt.comment_avatar,
                    'userName': cmt.user_name,
                    'floor': cmt.floor,
                    'createTime': cmt.create_time.strftime('%-m月%-d日 %H:%M'),
                    'likeCount': cmt.like_count,
                    'content': cmt.content,
                    'like': like,
                    'isAuthor': is_author
                }
                if cmt.delete == True:
                    cmt_data['delete'] = True
                    cmt_data['avatar'] = '/static/icons/avatar/nobody.svg'
                    cmt_data['userName'] = '這則留言已被刪除'
                    cmt_data['content'] = '<p>已經刪除的內容就像Scard一樣，錯過是無法再相見的！</p>'
                cmt_lst.append(cmt_data)
        else:
            cmts = db.session.execute('SELECT user.comment_avatar, comment.id, comment.user_name, comment.floor, comment.create_time, comment.like_count, comment.content\
            FROM comment INNER JOIN user ON comment.user_id=user.id\
            WHERE comment.post_id= :post_id',{'post_id': post_id}).all()
            like = False
            is_author = False
            for cmt in cmts:
                cmt_data = {
                    'id': cmt.id,
                    'avatar': cmt.comment_avatar,
                    'userName': cmt.user_name,
                    'floor': cmt.floor,
                    'createTime': cmt.create_time.strftime('%-m月%-d日 %H:%M'),
                    'likeCount': cmt.like_count,
                    'content': cmt.content,
                    'like': like,
                    'isAuthor': is_author
                }
                cmt_lst.append(cmt_data)
        db.session.close()
        return jsonify(cmt_lst), 200
    # except:
    #     db.session.close()
    #     return jsonify(ErrorData.server_error_data), 500

@api.route('/comment/<int:cmt_id>', methods=["PATCH"])
def patch_comment(cmt_id):
    cmt = Comment.query.filter_by(id=cmt_id).first()
    if 'user' in session and cmt:
        if cmt.user_id == session['user']['id']:
            req_data = request.json
            content = req_data['content']
            cmt.content = content
            db.session.commit()
            data = {'ok': True}
            return jsonify(data), 200
    return jsonify(ErrorData.no_sign_data), 403

@api.route('/comment/<int:cmt_id>', methods=["DELETE"])
def delete_comment(cmt_id):
    cmt = Comment.query.filter_by(id=cmt_id).first()
    if 'user' in session and cmt:
        if cmt.user_id == session['user']['id']:
            cmt.delete = True
            db.session.commit()
            data = {'ok':True}
            return jsonify(data), 200
    return jsonify(ErrorData.wrong_user_edit_data), 403


@api.route('/comment/<int:cmt_id>/like', methods=["PATCH"])
def patch_comment_like(cmt_id):
    try:
        if 'user' in session:
            user_id = session["user"]["id"]
            user_verify = session["user"]["verify_status"]
            if user_verify == 'stranger':
                return jsonify(ErrorData.verify_mail_data), 403

            like = CommentUserLike.query.filter_by(comment_id=cmt_id, user_id=user_id).first()
            if like:
                db.session.delete(like)
                cmt = Comment.query.filter_by(id=cmt_id).first()
                cmt.like_count -= 1            
            else:
                like = CommentUserLike(comment_id=cmt_id, user_id=user_id)
                db.session.add(like)
                cmt = Comment.query.filter_by(id=cmt_id).first()
                cmt.like_count += 1
            db.session.commit()
            data = {
                "likeCount": cmt.like_count
            }
            return jsonify(data), 200
            
        return jsonify(ErrorData.no_sign_data), 403
    except:
        db.session.close()
        return jsonify(ErrorData.server_error_data), 500