from flask import Blueprint
# from app import r
from models.model import Comment, CommentUserLike, Notification, Post, PostBoard, PostUserFollow, PostUserLike, User, Scard, Messages, Collage, CollageDepartment,  cache, db
api = Blueprint('api', __name__)
class ErrorData:
    no_sign_data = {
        "error": True,
        'title': '您尚未登入',
        'message': '想一起加入討論，要先登入 Scard 唷！',
        'confirm': '登入',
        'url': '/signup'
    }

    verify_mail_data = {
        'error': True, 
        'title': '帳號尚未啟用',
        'message': '請至信箱收取驗證信，並點擊驗證連結完成帳號啟用。',
        'confirm': '確認',
        'url': '/'
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
        'url': '#'
    }

    error_format_data = {
        "error": True,
        'title': '錯誤格式',
        'message': '你上傳的不是圖片喔，重新確認一下吧',
        'confirm': '確認',
        'url': '/new-post'
    }

    wrong_collage_data = {
        "error": True,
        "disable": True
    }

    wrong_board_data = {
        "error": True,
        'title': '看板選擇錯誤',
        'message': '你沒有選擇看板喔，重新選擇一次吧',
        'confirm': '確認',
        'url': '#'
    }

    wrong_name_data = {
        "error": True,
        'title': '名稱選擇錯誤',
        'message': '你沒有選擇名稱喔，重新選擇一次吧',
        'confirm': '確認',
        'url': '#'
    }

    wrong_content_data = {
        "error": True,
        'title': '文章缺乏內容',
        'message': '你的文章沒有標題或內容喔，快來補齊他們吧',
        'confirm': '確認',
        'url': '#'
    }

from . import user, profile, scard, message, new_post, index, post, comment, notification