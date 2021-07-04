from flask import request, jsonify, session
from sqlalchemy import or_
from . import ErrorData, api
from datetime import date, timedelta
import sys
sys.path.append("..")
from models.model import Messages, db, User, Scard, cache

my_profile_data = {
    'error': True,
    'title': '您尚未填寫自我介紹',
    'message': '想開啟抽卡人生，先去豐富自我介紹吧！',
    'confirm': '填寫自介',
    'url': '/my/profile'
}

tomorrow_scard_data = {
    "error": True,
    'title': '明天就能抽卡囉',
    'message': '待午夜開始，一段期限 24 小時的緣分即將展開。',
    'confirm': '返回首頁',
    'url': '/'
}

@api.route('/scard', methods=["GET"])
def get_scard():
    try:
        if 'user' in session:
            user_id = session["user"]["id"]
            user_verify = session["user"]["verify"]
            user_scard = session["user"]["scard"]

            # 若User欄位的verify為false，建議使用者轉移到basic_profile填寫頁面
            if user_verify == False:
                return jsonify(ErrorData.basic_profile_data), 403
                
            # 若是自我介紹還沒填完scard為false，建議使用者轉移到my_profile填寫頁面
            if user_scard == False:
                return jsonify(my_profile_data), 403

            yesterday = date.today() - timedelta(days=1)
            scard_1 = Scard.view_scard_1(user_id, yesterday)
            scard_2 = Scard.view_scard_2(user_id, yesterday)
            
            if scard_1:
                invited = False if scard_1.user_1_message is None else True
                is_friend = scard_1.is_friend
                match_id = scard_1.user_2
                message_room_id = scard_1.id
            elif scard_2:
                invited = False if scard_2.user_2_message is None else True
                is_friend = scard_2.is_friend
                match_id = scard_2.user_1
                message_room_id = scard_2.id
            # 今天沒有抽到卡，通知使用者將會參加明天的抽卡
            else:
                return jsonify(tomorrow_scard_data), 403

            match_user = User.view_user(match_id)
            
            data = {
                'isFriend': is_friend,
                'invited': invited,
                'messageRoomId': message_room_id,
                'avatar': match_user.avatar,
                'name': match_user.name,
                'collage': match_user.collage,
                'department': match_user.department,
                'interest': match_user.interest,
                'club': match_user.club,
                'course': match_user.course,
                'country': match_user.country,
                'worry': match_user.worry,
                'swap': match_user.swap,
                'wantToTry': match_user.want_to_try
            }
            return jsonify(data), 200
        # 沒有登入
        return jsonify(ErrorData.no_sign_data), 403
    # 伺服器錯誤
    except:
        return jsonify(ErrorData.server_error_data), 500


@api.route('/scard', methods=["POST"])
def invite_friend():
    if 'user' in session:
        data = request.json
        message = data['message']

        user_id = session['user']['id']
        yesterday = date.today() - timedelta(days=1)
        scard_1 = Scard.query.filter_by(user_1=user_id, create_date=yesterday).first()
        scard_2 = Scard.query.filter_by(user_2=user_id, create_date=yesterday).first()

        # 根據使用者是user_1還是user_2 填入不同的message欄位
        if scard_1:
            scard_1.user_1_message = message
            # 如果兩個欄位都是str（代表有被填寫），則該配對成為好友，並將給對方的第一句話增加到message table中
            if isinstance(scard_1.user_2_message, str):
                scard_1.is_friend = True
                message_1 = Messages(scard_id=scard_1.id, user_id=scard_1.user_1, message=scard_1.user_1_message)
                message_2 = Messages(scard_id=scard_1.id, user_id=scard_1.user_2, message=scard_1.user_2_message)
                db.session.add_all([message_1, message_2])

                # 刪除舊的卡友資訊快取，建立新快取
                cache.delete_memoized(Scard.view_scard_2, scard_1.user_2, yesterday)    
                scard = Scard.view_scard_2(scard_1.user_2, yesterday)

            # 刪除舊的卡友資訊快取，建立新快取
            cache.delete_memoized(Scard.view_scard_1, user_id, yesterday)    
            scard = Scard.view_scard_1(user_id, yesterday)
            
            data = {
                'ok': True,
                'isFriend': scard_1.is_friend,
                'messageRoomId': scard_1.id
            }
        
        else:
            scard_2.user_2_message = message
            # 如果兩個欄位都是str（代表有被填寫），則該配對成為好友
            if isinstance(scard_2.user_1_message, str):
                scard_2.is_friend = True
                message_1 = Messages(scard_id=scard_2.id, user_id=scard_2.user_1, message=scard_2.user_1_message)
                message_2 = Messages(scard_id=scard_2.id, user_id=scard_2.user_2, message=scard_2.user_2_message)
                db.session.add_all([message_1, message_2])
                # 刪除舊的卡友資訊快取，建立新快取
                cache.delete_memoized(Scard.view_scard_1, scard_2.user_1, yesterday)    
                scard = Scard.view_scard_1(scard_2.user_1, yesterday)

            # 刪除舊的卡友資訊快取，建立新快取
            cache.delete_memoized(Scard.view_scard_2, user_id, yesterday)    
            scard = Scard.view_scard_2(user_id, yesterday)

            data = {
                'ok': True,
                'isFriend': scard_2.is_friend,
                'messageRoomId': scard_2.id
            }
        db.session.commit()    

        return jsonify(data), 200
        
    return jsonify(ErrorData.no_sign_data), 403

@api.route('/scard/zeroing', methods=["PATCH"])
def zeroing_scard():
    try:
        if 'user' in session:
            user_id = session["user"]["id"]
            # 將days_no_open_scard歸0
            User.query.filter_by(id=user_id).update({User.days_no_open_scard: 0})
            db.session.commit()
            data = {
                "ok": True
            }
            return jsonify(data), 200
    except:
        return jsonify(ErrorData.server_error_data), 500


@api.route('/scard/<int:scard_id>', methods=["DELETE"])
def delete_friend(scard_id):
    if 'user' in session:
        data = request.json
        friend_id = data['friendID']
        user_id = session['user']['id']
        # print(user_id, friend_id, type(user_id), type(friend_id),scard_id ,type(scard_id))
        if user_id < friend_id:
            db.session.execute('DELETE FROM scard\
            WHERE id=:scard_id AND user_1=:user_id AND user_2=:friend_id', {
                'scard_id': scard_id, 'user_id': user_id, 'friend_id': friend_id
            })
            cache.delete_memoized(Scard.scard_from_1, Scard, scard_id, user_id)
        else:
            db.session.execute('DELETE FROM scard\
            WHERE id=:scard_id AND user_1=:friend_id AND user_2=:user_id', {
                'scard_id': scard_id, 'user_id': user_id, 'friend_id': friend_id
            })
            cache.delete_memoized(Scard.scard_from_2, Scard, scard_id, user_id)
        db.session.commit()
        data = {"ok": True}
        return jsonify(data), 200
        
    return jsonify(ErrorData.no_sign_data), 403