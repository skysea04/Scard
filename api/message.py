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
            last_messages = db.session.execute("SELECT scard_id, message, create_time, user_1, user_2 \
                FROM (SELECT * FROM messages ORDER BY id DESC LIMIT 9999) friend , scard \
                WHERE friend.scard_id = scard.id AND (scard.user_1=:id OR scard.user_2=:id) \
                GROUP BY scard_id \
                ORDER BY create_time DESC",
                {"id":user_id})

            # 半個朋友都沒有的狀況
            if not last_messages:
                return jsonify(have_no_friends_data), 400

            friend_list = []
            for last_message in last_messages:
                last_message = last_message._asdict()
                if user_id == last_message["user_1"]:
                    friend = User.view_user(last_message["user_2"])
                else:
                    friend = User.view_user(last_message["user_1"])
                
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
            
            message_room_1 = Scard.scard_from_1(id, user_id)
            message_room_2 = Scard.scard_from_2(id, user_id)

            if message_room_1: # 如果user_1 == user_id，
                user = User.view_user(message_room_1.user_1)
                friend = User.view_user(message_room_1.user_2)
            elif message_room_2: # 如果user_2 == user_id
                user = User.view_user(message_room_2.user_2)
                friend = User.view_user(message_room_2.user_1)
            else:  # 使用者亂入不屬於自己所有的訊息頻道 
                return jsonify(not_friend_data), 400

            user_data = {
                "id": user.id,
                "name": user.name,
                "avatar": user.avatar
            }
                # else:
            friend_data = {
                "id": friend.id,
                "name": friend.name,
                "avatar": friend.avatar,
                "collage": friend.collage,
                "department": friend.department,
                "birthday": friend.birthday.strftime("%-m月%-d日"),
                "relationship": friend.relationship,
                "interest": friend.interest,
                "club": friend.club,
                "course": friend.course,
                "country": friend.country,
                "worry": friend.worry,
                "swap": friend.swap,
                "wantToTry": friend.want_to_try
            }

            messages = db.session.execute('SELECT user_id, message, create_time FROM messages WHERE scard_id=:id ORDER BY id DESC', {"id":id})
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

