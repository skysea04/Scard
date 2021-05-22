from flask import request, jsonify, session
from . import api
import sys
sys.path.append("..")
from models.model import db, User

@api.route('/user', methods=["GET"])
def get_user():
    # 驗證使用者是否有登入
    if 'user' in session:
        data = {
            "id": session["user"]["id"],
            "verify": session["user"]["verify"]
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
        exist_user = User.query.filter_by(email=email).first()

        # 註冊成功 順便登入
        if not exist_user:
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            exist_user = User.query.filter_by(email=email).first()
            session["user"] = {
                "id": exist_user.id,
                "verify": exist_user.verify
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
                    "verify": exist_user.verify
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