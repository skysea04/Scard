from logging import debug
from flask import jsonify, session
from . import ErrorData, api, db
from datetime import datetime
# 這邊待捕啦 做不完ㄏ
@api.route('/notification', methods=["GET"])
def get_notification():
    print('get_notification', datetime.now().strftime("%H:%M"))
    if 'user' in session:
        user_id = session['user']['id']
        notes = db.session.execute('SELECT href, content, update_time\
        FROM notification INNER JOIN post_user_follow ON notification.id = post_user_follow.note_id\
        WHERE content IS NOT NULL AND user_id = :user_id ORDER BY update_time',
        {"user_id": user_id}).all()

        note_lst = []
        for note in notes:
            note_data = {
                "href": note.href,
                "msg": note.content,
                "time": note.update_time.strftime('%-m月%-d日 %H:%M')
            }
            note_lst.append(note_data)
        data = {"data": note_lst}
        return jsonify(data), 200

    return jsonify(ErrorData.no_sign_data), 403