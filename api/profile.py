from flask import request, jsonify, session
from . import api
import sys
sys.path.append("..")
from models.model import db, User

no_sign_data = {
    "error": True,
    "message": "要先登入唷"
}

@api.route('profile', methods=["GET"])
def get_profile():
    return 0

@api.route('profile', methods=["POST"])
def post_profile():
    if 'user' in session:
        user_id = session["user"]["id"]
        profile = request.json
        name = profile["name"]
        gender = profile["gender"]
        birthday = profile["birthday"]
        collage = profile["collage"]
        department = profile["department"]
        
        # 填寫不符規定的情況
        if name == '' or gender !=("male" or "female") or birthday == '' or collage == '' or department == '':
            input_error_data = {
                "error": True,
                "message": '資料填寫不符規定'
            }
            return jsonify(input_error_data), 400
        
        # 將資料添入資料庫，回傳ok資訊
        user = User.query.filter_by(id=user_id).first()
        user.verify = True
        user.name = name
        user.gender = gender
        user.birthday = birthday
        user.collage = collage
        user.department = department
        db.session.commit()

        data = {"ok": True}
        return jsonify(data), 200
        
    # 沒有登入
    return jsonify(no_sign_data), 403

@api.route('profile', methods=["PATCH"])
def patch_profile():
    return 0