from flask import jsonify, request, session
import io, boto3, re
from uuid import uuid4
from PIL import Image
from . import api, ErrorData, Post, PostBoard, User, Subscribe, db
s3 = boto3.client('s3')

@api.route('/new-post', methods=["GET"])
def get_new_post():
    if "user" in session:
        # print(session)
        user_verify = session["user"]["verify_status"]
        if user_verify == 'stranger':
            return jsonify(ErrorData.verify_mail_data), 403
        elif user_verify == 'mail':
            return jsonify(ErrorData.basic_profile_data), 403

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
            "collage": session["user"]["collage"],
            "department": session["user"]["department"],
            "avatar": session["user"]["commentAvatar"],
            "boardList": board_list
        }
        return jsonify(data), 200

    return jsonify(ErrorData.no_sign_data), 403

@api.route('/new-post', methods=["POST"])
def post_new_post():
    if "user" in session:
        user_id = session["user"]["id"]
        user_verify = session["user"]["verify_status"]
        if user_verify == 'stranger':
            return jsonify(ErrorData.verify_mail_data), 403
        elif user_verify == 'mail':
            return jsonify(ErrorData.basic_profile_data), 403
        
        req_data = request.json
        try:
            board_id = int(req_data["board"])
        except:
            return jsonify(ErrorData.wrong_board_data), 400
        select_name = req_data["name"]
        post_title = req_data["title"]
        post_content = req_data["content"]
        

        print('content', post_content)

        # 查看使用者是否有正確選擇board
        board = PostBoard.view_board(board_id)
        if not board:
            return jsonify(ErrorData.wrong_board_data), 400
        
        # 查看使用者是否有正確選擇發文名稱
        user = User.view_user(user_id)
        if select_name == 'full':
            user_name = f'{user.collage} {user.department}'
        elif select_name == 'collage':
            user_name = user.collage
        elif select_name == '匿名':
            user_name = '匿名'
        else:
            return jsonify(ErrorData.wrong_name_data), 400
        
        # 查看使用者是否有填寫文章標題或內容
        if post_title == '' or post_content == '<p><br></p>':
            return jsonify(ErrorData.wrong_content_data), 400

        # 抓到所有內文中的圖片檔案，如果有圖片則將第一筆圖片src放入資料庫
        imgs = re.findall(r"https://.{73}jpeg",post_content)
        if imgs == []:
        # 將文章更新到資料庫，回傳使用者成功資訊
            new_post = Post(board_id=board_id, user_id=user_id, user_name=user_name, title=post_title, content=post_content)
        else:
            new_post = Post(board_id=board_id, user_id=user_id, user_name=user_name, title=post_title, content=post_content, first_img = imgs[0])
        db.session.add(new_post)
        db.session.commit()

        print(new_post.content)
        
        new_subscribe = Subscribe(channel_id=f'post_{new_post.id}_poster', user_id=user_id)
        db.session.add(new_subscribe)
        db.session.commit()
        data = {
            'ok': True,
            'url': '/'
        }
        return jsonify(data), 200
        
    return jsonify(ErrorData.no_sign_data), 403

@api.route('/new-post/image', methods=["POST"])
def post_image():
    if "user" in session:
        user_verify = session["user"]["verify_status"]
        if user_verify == 'stranger':
            return jsonify(ErrorData.verify_mail_data), 403
        elif user_verify == 'mail':
            return jsonify(ErrorData.basic_profile_data), 403

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
                img.thumbnail((2000, 2000))
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
                return jsonify(ErrorData.server_error_data), 500
        
        return jsonify(ErrorData.error_format_data), 400

    return jsonify(ErrorData.no_sign_data), 403