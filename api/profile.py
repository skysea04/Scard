from flask import request, jsonify, session
from . import api
from uuid import uuid4
from PIL import Image
import sys, os, boto3, io

s3 = boto3.client('s3')

sys.path.append("..")
from models.model import db, User

no_sign_data = {
    "error": True,
    "message": "要先登入唷"
}

@api.route('/profile', methods=["GET"])
def get_profile():
    return 0

@api.route('/profile', methods=["POST"])
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



@api.route('/profile', methods=["PATCH"])
def patch_profile():
    return 0


@api.route('/profile/avatar', methods=["PATCH"])
def patch_avatar():
    if "user" in session:
        user_id = session["user"]["id"]
        file = request.files["avatar"]
        if file.filename != '':
            read_file = file.read()
            img = Image.open(io.BytesIO(read_file))
            img = img.convert('RGB')
            img.thumbnail((1000, 1000))

            in_mem_file = io.BytesIO()
            img.save(in_mem_file, format='jpeg')
            in_mem_file.seek(0)
            
            try:
                user = User.query.filter_by(id=user_id).first()
                avatar_folder = 'https://scard-bucket.s3-ap-northeast-1.amazonaws.com/avatar'

                # 如果舊avatar是default，直接將圖片上傳到s3，並將user.avatar改為新avatar連結
                if user.avatar == f'{avatar_folder}/default_avatar.jpeg':
                    avatar_name = "avatar/%s.jpeg" % (str(uuid4()))
                    user.avatar = f'{avatar_folder}/{avatar_name}'
                    s3.upload_fileobj(in_mem_file, "scard-bucket", avatar_name, ExtraArgs={'ContentType': "image/jpeg", 'ACL': "public-read"})
                    db.session.commit()

                # 舊avatar不是default，將圖片進行更新
                else:
                    avatar_name = f'avatar/{user.avatar.split("avatar/")[1]}'
                    s3.put_object(Body=in_mem_file, Bucket="scard-bucket", Key=avatar_name, ContentType="image/jpeg", ACL="public-read")
                data = {"ok": True}
                return jsonify(data), 200
            
            except:
                data = {
                    "error":True,
                    "message": "伺服器內部錯誤"
                }
                return jsonify(data), 500

        else:
            data = {
                "error": True,
                "message": "請放入圖片檔案喔"
            }
            return jsonify(data), 400

    return jsonify(no_sign_data), 403