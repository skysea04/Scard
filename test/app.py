# from flask import *
# from flask_sqlalchemy import SQLAlchemy
# import os
# app = Flask(__name__)

# app.config["SECRET_KEY"] = os.urandom(24).hex()
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://skysea:Rock8967@database-scard.comdtbthwj2y.ap-northeast-1.rds.amazonaws.com:3306/scard"
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping":True}
# db = SQLAlchemy(app)


# class User(db.Model):
#     __tablename__ = 'user'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(255), nullable=False)
#     email = db.Column(db.String(255), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)

#     def as_dict(self):
#         return{c.name: getattr(self, c.name) for c in self.__table__.columns}

# def count():
#     count = User.query.count()
#     print(count)
#     return '00'
# count()

a = None
b = 'aaa'

if isinstance(b, str) and isinstance(a, str):
    print('gogo')


