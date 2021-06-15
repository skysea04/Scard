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


@api.route('/profile', methods=["GET"])
def get_profile():
    # 查看是否登入
    if "user" in session:
        user_id = session["user"]["id"]
        user_verify = session["user"]["verify"]
        # 檢查使用者是否通過基本驗證
        if user_verify == False:
            return jsonify(basic_profile_data), 400

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
                s3_url = 'https://scard-bucket.s3-ap-northeast-1.amazonaws.com'
                cdn_url = 'https://d2lzngk4bddvz9.cloudfront.net'

                new_avatar_name = "avatar/%s.jpeg" % (str(uuid4()))
                # 如果舊avatar是default，直接將圖片上傳到s3，並將user.avatar改為新avatar連結
                if user.avatar == f'{cdn_url}/avatar/default_avatar.jpeg':
                    s3.upload_fileobj(in_mem_file, "scard-bucket", new_avatar_name, ExtraArgs={'ContentType': "image/jpeg", 'ACL': "public-read"})

                # 舊avatar不是default，將圖片進行更新
                else:
                    old_avatar_name = f'avatar/{user.avatar.split("avatar/")[1]}'
                    s3.delete_object(Bucket="scard-bucket", Key=old_avatar_name)
                    s3.upload_fileobj(in_mem_file, "scard-bucket", new_avatar_name, ExtraArgs={'ContentType': "image/jpeg", 'ACL': "public-read"})
                data = {
                    "ok": True, 
                    "src": f'{cdn_url}/{new_avatar_name}'
                }
                user.avatar = f'{cdn_url}/{new_avatar_name}'
                db.session.commit()
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
