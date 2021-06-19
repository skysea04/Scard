from flask import request, jsonify, session
from . import api
import sys
sys.path.append("..")
from models.model import Post, PostBoard, db

@api.route('/posts', methods=["GET"])
def get_posts():
    is_popular = request.args.get('popular')
    select_board = request.args.get('board')
    # 熱門render之後補
    if is_popular:
        return
    else:
        page = request.args.get('page')
        
        
    return 
