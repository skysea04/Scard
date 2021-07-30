from flask import request, jsonify
from . import api, db

@api.route('/posts', methods=["GET"])
def get_posts():
    is_popular = request.args.get('popular')
    select_board = request.args.get('board')
    # 熱門render之後補
    if is_popular == 'true':
        return
    else:
        page = int(request.args.get('page'))
        next_page = page + 1
        render_num = 30
        render_index = page * render_num
        # 在首頁render的情況
        if select_board == 'all':
            posts = db.session.execute('SELECT post.id, post.board_id, post.user_name, post.title, post.content, post.first_img, post.like_count, post.comment_count, postboard.show_name, user.comment_avatar \
                FROM ((post INNER JOIN postboard ON post.board_id = postboard.id)\
                INNER JOIN user ON post.user_id = user.id)\
                ORDER BY id DESC\
                LIMIT :index, :render_num', {'index': render_index, 'render_num': render_num})
            next_post = db.session.execute('SELECT id FROM post\
                ORDER BY id DESC\
                LIMIT :index, :render_num', {'index': render_index + render_num, 'render_num': 1}).first()
        # 在各看板render的情況
        else:
            posts = db.session.execute('SELECT post.id, post.board_id, post.user_name, post.title, post.content, post.first_img, post.like_count, post.comment_count, postboard.show_name, user.comment_avatar \
                FROM ((post INNER JOIN postboard ON post.board_id = postboard.id)\
                INNER JOIN user ON post.user_id = user.id)\
                WHERE postboard.id = :board\
                ORDER BY post.id DESC\
                LIMIT :index, :render_num', {'board': select_board, 'index': render_index, 'render_num': render_num})
            next_post = db.session.execute('SELECT post.id\
                FROM post INNER JOIN postboard ON post.board_id = postboard.id\
                WHERE postboard.id = :board\
                ORDER BY post.id DESC\
                LIMIT :index, :render_num', {'board': select_board, 'index': render_index + render_num, 'render_num': 1}).first()

        if not next_post:
            next_page = None
        
        post_list = []
        for post in posts:
            post = post._asdict()
            # print(post)
            post_data = {
                "url": f"/b/{post['board_id']}/p/{post['id']}",
                "avatar": post['comment_avatar'],
                "board": post['show_name'],
                "userName": post['user_name'],
                "title": post['title'],
                "content": post['content'],
                "img": post['first_img'],
                "likeCount": post['like_count'],
                "commentCount": post['comment_count']
            }
            post_list.append(post_data)
        
        data = {
            "data": post_list,
            "nextPage": next_page
        }
        return jsonify(data), 200
        