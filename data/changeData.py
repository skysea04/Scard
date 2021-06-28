import sys
sys.path.append("..")
from models.model import Collage, db
from app import app
db.__init__(app)
def changeCollName():
    colls =  Collage.query.all()
    for coll in colls:
        if '財團法人' in coll.name:
            print(coll.name.split('財團法人').pop())
            coll.name = coll.name.split('財團法人').pop()

    db.session.commit()
changeCollName()