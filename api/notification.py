from logging import debug
from flask import json, request, jsonify, session
from . import ErrorData, api
import sys
sys.path.append("..")
from models.model import Messages, db, User, Scard

# 這邊待捕啦 做不完ㄏ
@api.route('/notification', methods=["GET"])
def get_notification():
    if 'user' in session:
        user_id = session['user']['id']
        db.session.execute('')

    return jsonify(ErrorData.no_sign_data), 403