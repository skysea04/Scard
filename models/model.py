from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import expression
from flask_migrate import Migrate
from sqlalchemy import Index, text
from flask_caching import Cache
import os
from dotenv import load_dotenv
load_dotenv()

redis_host = os.getenv("REDIS_HOST")

cache = Cache(config={"CACHE_TYPE": "RedisCache", "CACHE_REDIS_HOST": redis_host})
db = SQLAlchemy()
migrate = Migrate(compare_type=True)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    verify = db.Column(db.Boolean, server_default=expression.false(), nullable=False)
    name = db.Column(db.String(255))
    gender = db.Column(db.Enum("male", "female"))
    birthday = db.Column(db.Date)
    collage = db.Column(db.String(255))
    department = db.Column(db.String(255))
    scard = db.Column(db.Boolean, server_default=expression.false(), nullable=False)
    avatar = db.Column(db.String(255), server_default="https://d2lzngk4bddvz9.cloudfront.net/avatar/default_avatar.jpeg")
    relationship = db.Column(db.Enum('secret', 'single', 'in_a_relationship', 'complicated', 'open_relationship', 'no_show'), default="no_show")
    interest = db.Column(db.Text)
    club = db.Column(db.Text)
    course = db.Column(db.Text)
    country = db.Column(db.Text)
    worry = db.Column(db.Text)
    swap = db.Column(db.Text)
    want_to_try = db.Column(db.Text)
    days_no_open_scard = db.Column(db.Integer, server_default=text("3"), nullable=False)
    match_list = db.Column(db.JSON, server_default=text('(JSON_ARRAY())'))
    comment_avatar = db.Column(db.String(255))
    verify_status = db.Column(db.Enum("stranger", "mail", 'basic', 'scard', 'admin'), server_default="stranger",  nullable=False)

    def as_dict(self):
        return{c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    @cache.memoize(259200)
    def view_user(cls, user_id):
        return User.query.filter_by(id=user_id).first()

Index('email_pwd_index', User.email, User.password)
Index('no_open_index', User.days_no_open_scard)


class Collage(db.Model):
    __tablename__ = 'collage'
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

class CollageDepartment(db.Model):
    __tablename__ = 'collage_department'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    collage_id = db.Column(db.String(255), db.ForeignKey('collage.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)

class Scard(db.Model):
    __tablename__ = 'scard'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_1 = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user_2 = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    create_date = db.Column(db.Date, server_default=text('(NOW())'))
    user_1_message = db.Column(db.String(255))
    user_2_message = db.Column(db.String(255))
    is_friend = db.Column(db.Boolean, server_default=expression.false(), nullable=False)

    def as_dict(self):
        return{c.name: getattr(self, c.name) for c in self.__table__.columns}

    # @classmethod
    @cache.memoize(86400)
    def view_scard_1(user_id, create_date):
        return Scard.query.filter_by(user_1=user_id, create_date=create_date).first()
    # @classmethod
    @cache.memoize(86400)
    def view_scard_2(user_id, create_date):
        return Scard.query.filter_by(user_2=user_id, create_date=create_date).first()
    
    @classmethod
    @cache.memoize(259200)
    def scard_from_1(cls, id, user_id):
        return Scard.query.filter_by(id=id, user_1=user_id).first()
    @classmethod
    @cache.memoize(259200)
    def scard_from_2(cls, id, user_id):
        return Scard.query.filter_by(id=id, user_2=user_id).first()

Index('user1_date_index', Scard.user_1, Scard.create_date)
Index('user2_date_index', Scard.user_2, Scard.create_date)

class Messages(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scard_id = db.Column(db.Integer, db.ForeignKey('scard.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, server_default=text('NOW()'))

    def as_dict(self):
        return{c.name: getattr(self, c.name) for c in self.__table__.columns}

class PostBoard(db.Model):
    __tablename__ = 'postboard'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sys_name = db.Column(db.String(255), unique=True, nullable=False)
    show_name = db.Column(db.String(255), unique=True, nullable=False)
    icon = db.Column(db.String(255), unique=True, nullable=False)
    rule = db.Column(db.Text)

    @cache.memoize(9999999999999)
    def view_board(board_id):
        return PostBoard.query.filter_by(id=board_id).first()

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    board_id = db.Column(db.Integer, db.ForeignKey('postboard.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user_name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    first_img = db.Column(db.String(255))
    create_time = db.Column(db.DateTime, server_default=text('NOW()'))
    like_count = db.Column(db.Integer, server_default=text("0"), nullable=False)
    comment_count = db.Column(db.Integer, server_default=text("0"), nullable=False)

class PostUserLike(db.Model):
    __tablename__ = 'post_user_like'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)

Index('user_post_index', PostUserLike.user_id, PostUserLike.post_id)

class PostUserFollow(db.Model):
    __tablename__ = 'post_user_follow'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    note_id = db.Column(db.String(255), db.ForeignKey('notification.id', ondelete='CASCADE'))

Index('user_post_index', PostUserFollow.user_id, PostUserFollow.post_id)

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user_name = db.Column(db.String(255), nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, server_default=text('NOW()'), nullable=False)
    like_count = db.Column(db.Integer, server_default=text("0"), nullable=False)
    
class CommentUserLike(db.Model):
    __tablename__ = 'comment_user_like'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'), nullable=False)

Index('comment_user_index', CommentUserLike.comment_id, CommentUserLike.user_id)

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.String(255), primary_key=True)
    content = db.Column(db.String(255))
    href = db.Column(db.String(255))
    update_time = db.Column(db.DateTime, server_default=text('NOW()'), nullable=False)
