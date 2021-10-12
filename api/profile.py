from flask import jsonify, request, session
import io, sys, boto3
from uuid import uuid4
from PIL import Image
from . import api, ErrorData, Collage, CollageDepartment, User, db, cache
s3 = boto3.client('s3')

@api.route('/profile', methods=["GET"])
def get_profile():
    # 查看是否登入
    if "user" in session:
        user_id = session["user"]["id"]
        user_verify = session["user"]["verify_status"]
        if user_verify == 'stranger':
            return jsonify(ErrorData.verify_mail_data), 403
        elif user_verify == 'mail':
            return jsonify(ErrorData.basic_profile_data), 403

        user = User.view_user(user_id)
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
        
    return jsonify(ErrorData.no_sign_data), 403


@api.route('/profile', methods=["POST"])
def post_profile():
    # 查看是否登入
    if 'user' in session:
        user_id = session["user"]["id"]
        profile = request.json
        name = profile["name"]
        gender = profile["gender"]
        birthday = profile["birthday"]
        coll_id = profile["collage"]
        dpt_id = profile["department"]
        # print(name, gender, birthday, collage, department)

        coll_dpt = db.session.execute('SELECT collage.name AS coll_name, collage_department.name AS dpt_name\
        FROM collage_department INNER JOIN collage ON collage_department.collage_id = collage.id\
        WHERE collage.id = :coll_id AND collage_department.id = :dpt_id', 
        {"coll_id": coll_id, "dpt_id": int(dpt_id)}).first()
        # 填寫不符規定的情況
        if name == '' or (gender !="male" and gender != "female") or birthday == '' or not coll_dpt:
            input_error_data = {
                "error": True,
                "message": '資料填寫不符規定'
            }
            return jsonify(input_error_data), 400
        
        # 將資料添入資料庫，回傳ok資訊
        user = User.query.filter_by(id=user_id).first()
        if user.verify_status == 'mail':
            user.verify_status = 'basic'
        user.name = name
        user.gender = gender
        user.birthday = birthday
        user.collage = coll_dpt.coll_name,
        user.department = coll_dpt.dpt_name
        if gender == 'male':
            user.comment_avatar = '/static/icons/avatar/male-mask.svg'
        elif gender == 'female':
            user.comment_avatar = '/static/icons/avatar/female-mask.svg'
        db.session.commit()

        cache.delete_memoized(User.view_user, User, user_id)
        user = User.view_user(user_id)
        session["user"]= False
        session["user"] = {
                    "id": user.id,
                    "verify_status": user.verify_status,
                    "collage": user.collage,
                    "department": user.department,
                    "commentAvatar": user.comment_avatar
                }
        data = {"ok": True}
        return jsonify(data), 200
        
    # 沒有登入
    return jsonify(ErrorData.no_sign_data), 403


@api.route('/profile', methods=["PATCH"])
def patch_profile():
    # 查看是否登入
    if "user" in session:
        user_id = session["user"]["id"]
        data = request.json
        relationship = data["relationship"]
        interest = data["interest"]
        club = data["club"]
        course = data["course"]
        country = data["country"]
        worry = data["worry"]
        swap = data["swap"]
        want_to_try = data["want_to_try"]
        user = User.query.filter_by(id=user_id).first()
        # 屏除必填項目字數少於25字的更新
        if len(interest) < 15 or len(swap) < 15 or len(want_to_try) < 15:
            data = {
                "error": True,
                "message": "必填項目不可少於15字"
            }
            return jsonify(data), 400

        # 將資料更新，並回傳ok資訊
        user.relationship = relationship
        user.interest = interest
        user.club = club
        user.course = course
        user.country = country
        user.worry = worry
        user.swap = swap
        user.want_to_try = want_to_try
        # 填寫過後就可以抽卡了
        user.verify_status = 'scard'
        db.session.commit()
        data = {"ok": True}

        # 清除原本該使用者的快取資料，重新存入快取
        cache.delete_memoized(User.view_user, User, user_id)
        user = User.view_user(user_id)
        session["user"]= False
        session["user"] = {
                    "id": user.id,
                    "verify_status": user.verify_status,
                    "collage": user.collage,
                    "department": user.department,
                    "commentAvatar": user.comment_avatar
                }

        return jsonify(data), 200

    return jsonify(ErrorData.no_sign_data), 403 


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
                cdn_url = 'https://d3vb6r08z9jp7h.cloudfront.net'
                # https://d2lzngk4bddvz9.cloudfront.net
                

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

    return jsonify(ErrorData.no_sign_data), 403


@api.route('/profile/collage', methods=['GET'])
def get_collage():
    print('get_collage')
    try:
        colls = Collage.query.order_by(Collage.id).all()
        coll_lst = []
        for coll in colls:
            coll_data = {
                "id": coll.id,
                "name": coll.name
            }
            coll_lst.append(coll_data)
        data = {
            "data": coll_lst
        }
        return jsonify(data),200
    except:
        return jsonify(ErrorData.server_error_data), 500

@api.route('/profile/<collage_id>/department', methods=["GET"])
def get_department(collage_id):
    print('get_department')
    try:
        if collage_id == ' ':
            return jsonify(ErrorData.wrong_collage_data), 400

        dpts = CollageDepartment.query.filter_by(collage_id=collage_id).all()
        dpt_lst = []
        for dpt in dpts:
            dpt_data = {
                "id": dpt.id,
                "name": dpt.name
            }
            dpt_lst.append(dpt_data)
        data = {
            "data": dpt_lst
        }
        return jsonify(data), 200
    except:
        return jsonify(ErrorData.server_error_data), 500