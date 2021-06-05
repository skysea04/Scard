from flask import *
from flask_socketio import SocketIO, join_room, send
import os
from dotenv import load_dotenv
load_dotenv()
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_host = os.getenv("MYSQL_HOST")
mysql_database = os.getenv("MYSQL_DATABASE")

app = Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:3306/{mysql_database}'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping":True}

socketio = SocketIO(app)
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
	if 'user' in session:
		return redirect(url_for('index'))
	return render_template("signup.html")

@app.route('/basicprofile')
def basic_profile():
    return render_template('basic-profile.html')

@app.route('/my/profile')
def my_profile():
    return render_template('my-profile.html')

@app.route('/scard')
def scard():
	return render_template('scard.html')

@app.route('/message')
def redirect_message():
	return redirect(url_for('message', id=1))

@app.route('/message/<id>')
def message(id):
	return render_template('message.html')

@socketio.on('message')
def handle_message(msg):
    print('get message:'+ msg)
    send(msg, broadcast=True)

if __name__ == '__main__':
	socketio.run(app, host='0.0.0.0',port=3000, debug=True)