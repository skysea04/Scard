from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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

    def as_dict(self):
        return{c.name: getattr(self, c.name) for c in self.__table__.columns}

