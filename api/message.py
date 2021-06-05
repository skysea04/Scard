from flask import request, jsonify, session
from sqlalchemy import or_
from . import api
from datetime import date
import sys
sys.path.append("..")
from models.model import Messages, db, User, Scard

no_sign_data = {
    "error": True,
    'title': '您尚未登入',
    'message': '想一起加入討論，要先登入 Scard 唷！',
    'confirm': '登入',
    'url': '/signup'
}

have_no_friends_data = {
    "error": True,
    "title": "尚無卡友",
    "message": "還沒有和任何一位同學成為卡友，快去把握今天的緣分吧",
    "confirm": "前往抽卡",
    "url": "/scard"
}

not_friend_data = {
    'error': True, 
    'title': '無此好友',
    'message': '你不是這位同學的好友，不能亂入唷',
    'confirm': '返回首頁',
    'url': '/'
}

server_error_data = {
    "error": True,
    'title': '錯誤訊息',
    'message': '伺服器內部錯誤',
    'confirm': '返回首頁',
    'url': '/'
}

@api.route('/friendlist', methods=["GET"])
def get_friendlist():
    # try:
        if 'user' in session:
            user_id = session['user']['id']
            # 根據使用者最後傳送或收到訊息的時間排續好友資訊
            last_messages = db.session.execute("SELECT scard_id, message, create_time, user_1, user_2 FROM \
                (SELECT * FROM messages ORDER BY id DESC LIMIT 9999) friend , scard \
                WHERE friend.scard_id = scard.id AND (scard.user_1=:id OR scard.user_2=:id) \
                GROUP BY scard_id",
                {"id":user_id})

            # 半個朋友都沒有的狀況
            if not last_messages:
                return jsonify(have_no_friends_data), 400

            friend_list = []
            for last_message in last_messages:
                last_message = last_message._asdict()
                if user_id == last_message["user_1"]:
                    friend = User.query.filter_by(id=last_message["user_2"]).first()
                else:
                    friend = User.query.filter_by(id=last_message["user_1"]).first()
                
                friend_data = {
                    "name": friend.name,
                    "avatar": friend.avatar,
                    "message": last_message["message"],
                    "time": last_message["create_time"].strftime("%-m月%-d日 %H:%M"),
                    "messageRoomId": last_message["scard_id"]
                }
                friend_list.append(friend_data)
                
            data = {
                "data": friend_list
            }
            return jsonify(data), 200
            
        # 沒有登入
        return jsonify(no_sign_data), 403
    # 伺服器錯誤
    # except:
    #     return jsonify(server_error_data), 500
    

@api.route('/message/<id>', methods=["GET"])
def get_message(id):
    # try:
        if 'user' in session:
            user_id = session['user']['id']
            # messages = Messages.query.filter_by(scard_id=id).order_by(Messages.id).all()
            messages = db.session.execute('SELECT user_id, message, create_time FROM messages WHERE scard_id=:id ORDER BY id DESC;', {"id":id})
            
            # 使用者亂入其他頁面 
            if not messages:
                return jsonify(not_friend_data), 400

            # 抓取message中兩個
            users = db.session.execute('SELECT user.* \
                FROM scard INNER JOIN user WHERE (scard.user_1=user.id or scard.user_2=user.id)\
                AND scard.id=:id', {"id":id})
            
            for user in users:
                user = user._asdict()
                # print(user)
                if user_id == user["id"]:
                    user_data = {
                        "id": user["id"],
                        "name": user["name"],
                        "avatar": user["avatar"]
                    }
                else:
                    friend_data = {
                        "id": user["id"],
                        "name": user["name"],
                        "avatar": user["avatar"],
                        "collage": user["collage"],
                        "department": user["department"],
                        "birthday": user["birthday"].strftime("%-m月%-d日"),
                        "relationship": user["relationship"],
                        "interest": user["interest"],
                        "club": user["club"],
                        "course": user["course"],
                        "country": user["country"],
                        "worry": user["worry"],
                        "swap": user["swap"],
                        "wantToTry": user["want_to_try"]
                    }

            message_list = []
            for message in messages:
                message = message._asdict()
                message_data = {
                    "userId": message["user_id"],
                    "message": message["message"],
                    "time": message["create_time"].strftime("%-m月%-d日 %H:%M")
                }
                message_list.append(message_data)
            data = {
                "user": user_data,
                "friend": friend_data,
                "data": message_list
            }
            return jsonify(data), 200
        # 沒有登入
        return jsonify(no_sign_data), 403
    # 伺服器錯誤
    # except:
    #     return jsonify(server_error_data), 500

