from flask import *
from flask_socketio import SocketIO, join_room, send
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.engine import url
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
from models.model import Messages, db, migrate, cache
db.init_app(app)
migrate.init_app(app, db)

cache.init_app(app)

# 向app註冊api的藍圖
from api import api
app.register_blueprint(api, url_prefix="/api")

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/new-post')
def post():
	if 'user' in session:
		return render_template('new-post.html')
	return redirect(url_for('signup'))

@app.route('/signup')
def signup():
	if 'user' in session:
		return redirect(url_for('index'))
	return render_template('signup.html')

@app.route('/basicprofile')
def basic_profile():
	if 'user' in session:
		return render_template('basic-profile.html')
	return redirect(url_for('signup'))

@app.route('/my/profile')
def my_profile():
	if 'user' in session:
		return render_template('my-profile.html')
	return redirect(url_for('signup'))

@app.route('/scard')
def scard():
	if 'user' in session:
		return render_template('scard.html')
	return redirect(url_for('signup'))

@app.route('/message')
def redirect_message():
	if "user" in session:
		user_id = session["user"]["id"]
		# 找尋最近期通信過的朋友
		message_id = db.session.execute("SELECT scard_id\
			FROM (SELECT * FROM messages ORDER BY id DESC LIMIT 9999) friend , scard \
			WHERE friend.scard_id = scard.id AND (scard.user_1=:id OR scard.user_2=:id) \
			GROUP BY scard_id \
			LIMIT 1",
			{"id":user_id}).first()
		# 如果有朋友，轉移到該位朋友的頻道
		if message_id:
			message_id = message_id[0]
			return redirect(url_for('message', id=message_id))

	return redirect(url_for('index'))

@app.route('/message/<id>')
def message(id):
	if 'user' in session:
		return render_template('message.html')
	return redirect(url_for('signup'))

@socketio.on('message')
def handle_message(msg):
    print('get message:'+ msg)
    send(msg, broadcast=True)

@socketio.on('join_room')
def handle_join_room(room_id):
	join_room(room_id)
	send(room_id)

@socketio.on('send_message')
def handle_send_message(data):
	data["time"] = datetime.now().strftime("%-m月%-d日 %H:%M")
	socketio.emit('receive_message', data, room=data["room"])
	message = Messages(scard_id=data["room"], user_id=data["id"], message=data["message"])
	db.session.add(message)
	db.session.commit()


if __name__ == '__main__':
	socketio.run(app, host='0.0.0.0',port=8000)
