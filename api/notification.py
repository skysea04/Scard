from flask import jsonify, session
from . import ErrorData, api, db, Subscribe
import sys, json
sys.path.append("..")
from app import r
# 這邊待捕啦 做不完ㄏ
@api.route('/notification', methods=["GET"])
def get_notification():
    if 'user' in session:
        user_id = session['user']['id']
        note_lst = []
        notes = r.hvals(f'user_{user_id}_note')
        for note in notes:
            note_lst.append(json.loads(note))
        note_lst = sorted(note_lst, key= lambda n:n['time'])
        data = {"data": note_lst}
        return jsonify(data), 200

    return jsonify(ErrorData.no_sign_data), 403

# 獲取使用者追蹤（訂閱）的頻道
@api.route('/my/sub', methods=['GET'])
def get_my_sub():
    if 'user' in session:
        user_id = session['user']['id']
        subs = Subscribe.query.filter_by(user_id=user_id).all()
        # posts = PostUserFollow.query.filter_by(user_id=user_id).all()
        sub_lst = []
        for sub in subs:
            sub_lst.append(sub.channel_id)
        data = {
            'data': sub_lst
        }
        return jsonify(data), 200
    return jsonify(ErrorData.no_sign_data), 403