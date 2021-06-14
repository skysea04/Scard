from flask import jsonify, request, session
import io, sys, boto3
from uuid import uuid4
from PIL import Image

from . import api

s3 = boto3.client('s3')

sys.path.append("..")
from models.model import PostBoard, User, db, cache

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

server_error_data = {
    "error": True,
    'title': '錯誤訊息',
    'message': '伺服器內部錯誤',
    'confirm': '重新整理',
    'url': '/new-post'
}

error_format_data = {
    "error": True,
    'title': '錯誤格式',
    'message': '你上傳的不是圖片喔，重新確認一下吧',
    'confirm': '確認',
    'url': '/new-post'
}


@api.route('/new-post', methods=["GET"])
def get_new_post():
    if "user" in session:
        user_id = session["user"]["id"]
        user_verify = session["user"]["verify"]
        if user_verify == False:
            return jsonify(basic_profile_data), 403
        
        user_collage = session["user"]["collage"]
        user_department = session["user"]["department"]

        # 搜集所有po文版資訊
        board_list = []
        boards = PostBoard.query.all()
        for board in boards:
            board_dict = {
                "boardId": board.id,
                "showName": board.show_name
            }
            board_list.append(board_dict)

        data = {
            "collage": user_collage,
            "department": user_department,
            "boardList": board_list
        }
        return jsonify(data), 200

    return jsonify(no_sign_data), 403

@api.route('/new-post', methods=["POST"])
def post_new_post():
    if "user" in session:
        user_id = session["user"]["id"]
        user_verify = session["user"]["verify"]
        if user_verify == False:
            return jsonify(basic_profile_data), 403
        
        

    return jsonify(no_sign_data), 403

@api.route('/new-post/image', methods=["POST"])
def post_image():
    if "user" in session:
        user_verify = session["user"]["verify"]
        if user_verify == False:
            return jsonify(basic_profile_data), 403

        file = request.files["image"]
        allow_file = ['png', 'jpg', 'jpeg', 'gif']
        file_format = file.filename.rsplit('.', 1)[1]
        if file_format in allow_file:
            if file_format == 'gif':
                in_mem_file = file
            else:
                read_file = file.read()
                img = Image.open(io.BytesIO(read_file))
                img = img.convert('RGB')
                img.thumbnail((1000, 1000))
                file_format = 'jpeg'

                in_mem_file = io.BytesIO()
                img.save(in_mem_file, format=file_format)
                in_mem_file.seek(0)
            
            try:
                cdn_url = 'https://d2lzngk4bddvz9.cloudfront.net'
                image_name = "image/%s.%s" % (str(uuid4()), file_format)
                s3.upload_fileobj(in_mem_file, "scard-bucket", image_name, ExtraArgs={'ContentType': f"image/{file_format}", 'ACL': "public-read"})

                data = {
                    "ok": True, 
                    "src": f'{cdn_url}/{image_name}'
                }
                return jsonify(data), 200
            
            except:
                return jsonify(server_error_data), 500
        
        return jsonify(error_format_data), 400

    return jsonify(no_sign_data), 403