from flask import jsonify, request, session
import io, sys, boto3
from uuid import uuid4
from PIL import Image

from . import api

s3 = boto3.client('s3')

sys.path.append("..")
from models.model import User, db, cache

no_sign_data = {
    "error": True,
    "message": "要先登入唷"
}

@api.route('/verify', methods=["GET"])
def verify_user():
    # 查看是否登入
    if "user" in session:
        user_id = session["user"]["id"]
        user = User.view_user(user_id)
        # user = User.query.filter_by(id=user_id).first()
        # 檢查使用者是否通過基本驗證
        if user.verify == False:
            data = {
                "error": True,
                "message": "要先填寫基本資料唷"
            }
            return jsonify(data), 400
        # 通過認證
        data = {"ok": True}
        return jsonify(data), 200
        
    return jsonify(no_sign_data), 403


@api.route('/profile', methods=["GET"])
def get_profile():
    # 查看是否登入
    if "user" in session:
        user_id = session["user"]["id"]
        user = User.view_user(user_id)
        # user = User.query.filter_by(id=user_id).first()
        data = {
            "avatar": user.avatar,
            "name": user.name,
            "collage": user.collage,
            "department": user.department,
            "relationship": user.relationship,
            "interest": user.interest,
            "club": user.club,
            "course": user.course,
            "country": user.country,
            "worry": user.worry,
            "swap": user.swap,
            "want_to_try": user.want_to_try
        }
        return jsonify(data), 200
        
    return jsonify(no_sign_data), 403

@api.route('/profile', methods=["POST"])
def post_profile():
    # 查看是否登入
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

        cache.delete_memoized(User.view_user, User, user_id)
        user = User.view_user(user_id)

        data = {"ok": True}
        return jsonify(data), 200
        
    # 沒有登入
    return jsonify(no_sign_data), 403



@api.route('/profile', methods=["PATCH"])
def patch_profile():
    # 查看是否登入
    if "user" in session:
        user_id = session["user"]["id"]
        data = request.json
        collage = data["collage"]
        department = data["department"]
        relationship = data["relationship"]
        interest = data["interest"]
        club = data["club"]
        course = data["course"]
        country = data["country"]
        worry = data["worry"]
        swap = data["swap"]
        want_to_try = data["want_to_try"]
        user = User.query.filter_by(id=user_id).first()

        # 屏除將學校與系所欄位刪除的更新
        if collage == '' or department == '':
            data = {
                "error": True,
                "message": "學校與系所一定要填喔"
            }
            return jsonify(data), 400
        else:
            # 屏除必填項目字數少於25字的更新
            if len(interest) < 25 or len(swap) < 25 or len(want_to_try) < 25:
                data = {
                    "error": True,
                    "message": "必填項目不可少於25字"
                }
                return jsonify(data), 400

            # 將資料更新，並回傳ok資訊
            user.collage = collage
            user.department = department
            user.relationship = relationship
            user.interest = interest
            user.club = club
            user.course = course
            user.country = country
            user.worry = worry
            user.swap = swap
            user.want_to_try = want_to_try
            # 填寫過後就可以抽卡了
            user.scard = True
            db.session.commit()
            data = {"ok": True}

            # 清除原本該使用者的快取資料，重新存入快取
            cache.delete_memoized(User.view_user, User, user_id)
            user = User.view_user(user_id)

            return jsonify(data), 200

    return jsonify(no_sign_data), 403 


@api.route('/profile/avatar', methods=["PATCH"])
def patch_avatar():
    if "user" in session:
        user_id = session["user"]["id"]
        file = request.files["avatar"]
        allow_file = ['png', 'jpg', 'jpeg', 'gif']
        if file.filename.rsplit('.', 1)[1] in allow_file:
            read_file = file.read()
            img = Image.open(io.BytesIO(read_file))
            img = img.convert('RGB')
            img.thumbnail((1000, 1000))

            in_mem_file = io.BytesIO()
            img.save(in_mem_file, format='jpeg')
            in_mem_file.seek(0)
            
            try:
                user = User.query.filter_by(id=user_id).first()
                avatar_folder = 'https://scard-bucket.s3-ap-northeast-1.amazonaws.com'
                avatar_name = "avatar/%s.jpeg" % (str(uuid4()))
                # 如果舊avatar是default，直接將圖片上傳到s3，並將user.avatar改為新avatar連結
                if user.avatar == f'{avatar_folder}/avatar/default_avatar.jpeg':
                    user.avatar = f'{avatar_folder}/{avatar_name}'
                    s3.upload_fileobj(in_mem_file, "scard-bucket", avatar_name, ExtraArgs={'ContentType': "image/jpeg", 'ACL': "public-read"})
                    db.session.commit()

                # 舊avatar不是default，將圖片進行更新
                else:
                    avatar_name = f'avatar/{user.avatar.split("avatar/")[1]}'
                    s3.put_object(Body=in_mem_file, Bucket="scard-bucket", Key=avatar_name, ContentType="image/jpeg", ACL="public-read")
                data = {
                    "ok": True, 
                    "src": f'{avatar_folder}/{avatar_name}'
                }
                # 清除原本該使用者的快取資料，重新存入快取
                cache.delete_memoized(User.view_user, User, user_id)
                user = User.view_user(user_id)
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
