from flask import request, jsonify, session
from . import ErrorData, api, User, db
import sys, smtplib, email.message as email_message

sys.path.append("..")
# from models.model import db, User
from app import mail_username, mail_password

mail_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
mail_server.login(mail_username, mail_password)

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

@api.route('/user', methods=["GET"])
def get_user():
    # 驗證使用者是否有登入
    if 'user' in session:
        data = {
            "id": session["user"]["id"],
        }
        return jsonify(data), 200

    # 使用者沒有登入
    data = {
        "data": None
    }
    return jsonify(data), 200

@api.route('/user', methods=["POST"])
def post_user():
    try:
        data = request.json
        email = data['email']
        password = data['password']
        from_api = data['fromAPI']
        exist_user = User.query.filter_by(email=email).first()

        # 註冊成功 順便登入
        if not exist_user:
            if from_api:
                new_user = User(email=email, password=password, verify_status='mail')
            else:
                new_user = User(email=email, password=password)

                mail_msg = email_message.EmailMessage()
                mail_msg["From"] = mail_username
                mail_msg["To"] = email
                mail_msg["Subject"] = 'Scard驗證信箱'
                href = f'https://scard.skysea.fun/mailverify/{email}'
                mail_msg.add_alternative(f'\
                <h3>立即啟用你的Scard帳號</h3>\
                <p>感謝你/妳的註冊，我們想確認你所輸入的註冊信箱是正確的。</p>\
                <p>點擊下方網址完成信箱驗證，即可馬上啟用Scard帳號喔！</p>\
                <a href="{href}">{href}</a>\
                    ', subtype='html')
                mail_server.send_message(mail_msg)

            db.session.add(new_user)
            db.session.commit()
            exist_user = User.query.filter_by(email=email).first()
            session["user"] = {
                "id": exist_user.id,
                "email": exist_user.email,
                "verify": exist_user.verify,
                "scard": exist_user.scard,
                "verify_status": exist_user.verify_status,
                "collage": exist_user.collage,
                "department": exist_user.department,
                "commentAvatar": exist_user.comment_avatar
            }
            data = {
                "ok": True
            }
            return jsonify(data), 200

        # 該email已經在使用者名單內
        else:
            # 密碼也正確，讓他登入
            if exist_user.password == password:
                session["user"] = {
                    "id": exist_user.id,
                    "email": exist_user.email,
                    "verify": exist_user.verify,
                    "scard": exist_user.scard,
                    "verify_status": exist_user.verify_status,
                    "collage": exist_user.collage,
                    "department": exist_user.department,
                    "commentAvatar": exist_user.comment_avatar
                }
                data = {
                    "ok": True
                }
                return jsonify(data), 200

            # 密碼錯誤，顯示錯誤訊息
            data = {
                "error": True,
                "message": "信箱或密碼錯誤"
            }
            return jsonify(data), 403

    # 伺服器錯誤
    except:
        data = {
            "error": True,
            "message": "伺服器內部錯誤"
        }
        return jsonify(data), 500

@api.route('/user', methods=["DELETE"])
def delete_user():
    # 登出
    session.pop('user')
    data = {"ok": True}
    return jsonify(data), 200

@api.route('/verify', methods=["GET"])
def verify_user():
    if 'user' in session:
        # verify = session["user"]["verify"]
        # scard = session["user"]["scard"]
        href = request.args.get('a')
        verify = session['user']['verify_status']
        if verify == 'stranger':
            return jsonify(ErrorData.verify_mail_data), 403
        elif verify == 'mail':
            return jsonify(ErrorData.basic_profile_data), 403
        elif verify == 'basic':
            if href == 'scard' or href == 'message':
                return jsonify(my_profile_data), 403
        data = {
            "ok": True,
            "url": f'/{href}'    
        }
        return jsonify(data), 200
    
    return jsonify(ErrorData.no_sign_data), 403