from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import date, datetime
from sqlalchemy import Index
db = SQLAlchemy()
migrate = Migrate(compare_type=True)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    verify = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(255))
    gender = db.Column(db.Enum("male", "female"))
    birthday = db.Column(db.Date)
    collage = db.Column(db.String(255))
    department = db.Column(db.String(255))
    scard = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(255), default="https://scard-bucket.s3-ap-northeast-1.amazonaws.com/avatar/default_avatar.jpeg")
    relationship = db.Column(db.Enum('secret', 'single', 'in_a_relationship', 'complicated', 'open_relationship', 'no_show'), default="no_show")
    interest = db.Column(db.Text)
    club = db.Column(db.Text)
    course = db.Column(db.Text)
    country = db.Column(db.Text)
    worry = db.Column(db.Text)
    swap = db.Column(db.Text)
    want_to_try = db.Column(db.Text)
    days_no_open_scard = db.Column(db.Integer, default=3, nullable=False)

    def as_dict(self):
        return{c.name: getattr(self, c.name) for c in self.__table__.columns}

Index('email_pwd_index', User.email, User.password)
Index('no_open_index', User.days_no_open_scard)

class Scard(db.Model):
    __tablename__ = 'scard'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_1 = db.Column(db.Integer, nullable=False)
    user_2 = db.Column(db.Integer, nullable=False)
    create_date = db.Column(db.Date, default=date.today())
    user_1_message = db.Column(db.String(255))
    user_2_message = db.Column(db.String(255))
    is_friend = db.Column(db.Boolean, default=False)

    def as_dict(self):
        return{c.name: getattr(self, c.name) for c in self.__table__.columns}
    

class Messages(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scard_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now())

    def as_dict(self):
        return{c.name: getattr(self, c.name) for c in self.__table__.columns}