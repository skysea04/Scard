from flask import *
import os

app = Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["SECRET_KEY"] = '123'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://skysea:Rock8967@database-scard.comdtbthwj2y.ap-northeast-1.rds.amazonaws.com:3306/scard'
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping":True}

from models.model import db, migrate
db.init_app(app)
migrate.init_app(app, db)

# 向app註冊api的藍圖
from api import api
app.register_blueprint(api, url_prefix="/api")

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/signup")
def signup():
	return render_template("signup.html")

@app.route('/basicprofile')
def basic_profile():
    return render_template('basic-profile.html')

@app.route('/my/profile')
def my_profile():
    return render_template('my-profile.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=3000, debug=True)