import sys
sys.path.append("..")
from models.model import User, db
from app import app
from argon2 import PasswordHasher
db.__init__(app)
ph = PasswordHasher()
def changeUserPwd():
    users = User.query.all()
    for user in users:
        user.password = ph.hash(user.password)
        print(user.id)
    db.session.commit()

changeUserPwd()
    