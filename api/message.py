from flask import request, jsonify, session
from . import ErrorData, api, db, User, Scard
# import sys
# sys.path.append("..")
# from models.model import Messages, db, User, Scard

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

@api.route('/message_room', methods=['GET'])
def get_message_room():
    if 'user' in session:
        user_id = session['user']['id']
        rooms = db.session.execute('SELECT id FROM scard WHERE (user_1=:id OR user_2=:id) AND is_friend IS true', {"id": user_id}).all()
        room_list = []
        for room in rooms:
            room_list.append(room.id)
        data = {
            "data": room_list
        }
        return jsonify(data), 200
    return jsonify(ErrorData.no_sign_data), 403

@api.route('/friendlist', methods=["GET"])
def get_friendlist():
    try:
        if 'user' in session:
            user_id = session['user']['id']
            # 根據使用者最後傳送或收到訊息的時間排續好友資訊
            last_messages = db.session.execute("SELECT scard_id, message, create_time, user_1, user_2 \
                FROM (SELECT * FROM messages ORDER BY id DESC LIMIT 9999) friend , scard \
                WHERE friend.scard_id = scard.id AND (scard.user_1=:id OR scard.user_2=:id) \
                GROUP BY scard_id \
                ORDER BY create_time DESC", {"id":user_id})

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
        return jsonify(ErrorData.no_sign_data), 403
    # 伺服器錯誤
    except:
        return jsonify(ErrorData.server_error_data), 500
    

@api.route('/message/<int:id>', methods=["GET"])
def get_message(id):
    try:
        if request.args.get('page'):
            page = int(request.args.get('page'))
            render_num = 30
            first_index = page * render_num
            next_page = page + 1
        if 'user' in session:
            user_id = session['user']['id']
            
            message_room_1 = Scard.scard_from_1(id, user_id)
            message_room_2 = Scard.scard_from_2(id, user_id)
            # print(message_room_1, message_room_2)

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

            messages = db.session.execute('SELECT user_id, message, create_time FROM messages WHERE scard_id=:id ORDER BY id DESC LIMIT :index, :render_num', {"id":id, "index":first_index, "render_num":render_num})
            next_message = db.session.execute('SELECT user_id, message, create_time FROM messages WHERE scard_id=:id ORDER BY id DESC LIMIT :index, :render_num', {"id":id, "index":first_index + render_num, "render_num":1}).first()
            # for message in next_messages:
            if next_message == None: 
                next_page = None
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
                "data": message_list,
                "nextPage": next_page
            }
            return jsonify(data), 200
        # 沒有登入
        return jsonify(ErrorData.no_sign_data), 403
    # 伺服器錯誤
    except:
        return jsonify(ErrorData.server_error_data), 500

