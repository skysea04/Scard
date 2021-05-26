from flask import request, jsonify, session
from sqlalchemy import or_
from . import api
from datetime import date
import sys
sys.path.append("..")
from models.model import db, User, Scard



no_sign_data = {
    "error": True,
    'title': '您尚未登入',
    'message': '想一起加入討論，要先登入 Scard 唷！',
    'confirm': '登入',
    'url': '/signup'
}

basic_profile_data = {
    'error': True, 
    'title': '您尚未填寫基本資料',
    'message': '想一起加入討論，要先填完基本資料唷！',
    'confirm': '填資料去',
    'url': '/basicprofile'
}

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

server_error_data = {
    "error": True,
    'title': '錯誤訊息',
    'message': '伺服器內部錯誤',
    'confirm': '返回首頁',
    'url': '/'
}

@api.route('/scard', methods=["GET"])
def get_scard():
    try:
        if 'user' in session:
            user_id = session['user']['id']

            user = User.query.filter_by(id=user_id).first()
            # 若User欄位的verify為false，建議使用者轉移到basic_profile填寫頁面
            if user.verify == False:
                return jsonify(basic_profile_data), 403
                
            # 若是自我介紹還沒填完scard為false，建議使用者轉移到my_profile填寫頁面
            if user.scard == False:
                return jsonify(my_profile_data), 403
                                
            scard = Scard.query.filter(or_(Scard.user_1 == user_id, Scard.user_2 == user_id)).filter_by(create_date=date.today()).first()
            # 將days_no_open_card歸0
            user.days_no_open_card = 0
            db.session.commit()
            
            # 如果今天沒有抽到卡，通知使用者將會參加明天的抽卡
            if not scard:
                return jsonify(tomorrow_scard_data), 403
            
            user_message = scard.user_1_message if user_id == scard.user_1 else scard.user_2_message
            invited = False if user_message is None else True
            is_friend = scard.is_friend
            match_id = scard.user_2 if user_id == scard.user_1 else scard.user_1
            match_user = User.query.filter_by(id=match_id).first()
            
            data = {
                'isFriend': is_friend,
                'invited': invited,
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
        return jsonify(no_sign_data), 403
    # 伺服器錯誤
    except:
        return jsonify(server_error_data), 500


@api.route('/scard', methods=["POST"])
def invite_friend():
    if 'user' in session:
        data = request.json
        message = data['message']

        user_id = session['user']['id']
        scard = Scard.query.filter(or_(Scard.user_1 == user_id, Scard.user_2 == user_id)).filter_by(create_date=date.today()).first()
        # 根據使用者是user_1還是user_2 填入不同的message欄位
        if user_id == scard.user_1:
            scard.user_1_message = message
        else:
            scard.user_2_message = message
        
        # 如果兩個欄位都是str（代表有被填寫），則該配對成為好友
        if isinstance(scard.user_1_message, str) and isinstance(scard.user_1_message, str):
            scard.is_friend = True
        db.session.commit()    

        data = {
            'ok': True,
            'isFriend': scard.is_friend
        }
        return jsonify(data), 200
        
    return jsonify(no_sign_data), 403