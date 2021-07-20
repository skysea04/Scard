from flask import request, jsonify, session
from argon2 import PasswordHasher
from . import ErrorData, api, User, db
import sys, smtplib, email.message as email_message

ph = PasswordHasher()
sys.path.append("..")
from app import mail_username, mail_password
mail_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
mail_server.login(mail_username, mail_password)

my_profile_data = {
    'error': True,
    'title': '您尚未填寫自我介紹',
    'message': '想開啟抽卡人生，先去豐富自我介紹吧！',
    'confirm': '填寫自介',
    'url': '/my/profile'
}

# 寄信給使用者驗證帳號
def send_mail_to_verify(email):
    try:
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
    except:
        return '送信失敗'

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
        hash_pwd = ph.hash(password)

        # 註冊成功 順便登入
        if not exist_user:
            if from_api:
                new_user = User(email=email, password=hash_pwd, verify_status='mail')
            else:
                new_user = User(email=email, password=hash_pwd)
                # 寄信給使用者
                send_mail_to_verify(email)

            db.session.add(new_user)
            db.session.commit()
            exist_user = User.query.filter_by(email=email).first()
            session["user"] = {
                "id": exist_user.id,
                "email": exist_user.email,
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
            try: 
                ph.verify(exist_user.password, password)
                session["user"] = {
                    "id": exist_user.id,
                    "email": exist_user.email,
                    "verify_status": exist_user.verify_status,
                    "collage": exist_user.collage,
                    "department": exist_user.department,
                    "commentAvatar": exist_user.comment_avatar
                }
                data = {
                    "ok": True
                }
                return jsonify(data), 200
            except:
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

@api.route('/mailverify', methods=["POST"])
def verify_user_email():
    if 'user' in session:
        email = session['user']['email']
        try:
            send_mail_to_verify(email)
            return jsonify({
                'ok': True,
                'message': '已經重新寄送驗證信囉，趕快去確認吧！'
            }), 200
        except:
            return jsonify({
                'error': True,
                'message': '信件送出失敗，請稍後再試'
            }), 500
    return jsonify(ErrorData.no_sign_data), 403

@api.route('/verify', methods=["GET"])
def get_user_verify():
    if 'user' in session:
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
