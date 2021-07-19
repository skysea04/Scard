from logging import debug
from flask import *
from flask_socketio import SocketIO, join_room, leave_room, emit
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_host = os.getenv("MYSQL_HOST")
mysql_database = os.getenv("MYSQL_DATABASE")
redis_host = os.getenv("REDIS_HOST")
mail_username = os.getenv('MAIL_USERNAME')
mail_password = os.getenv('MAIL_PASSWORD')
from redis import Redis
r = Redis(host=redis_host, port=6379)


app = Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:3306/{mysql_database}?charset=utf8mb4'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping":True}


socketio = SocketIO(app)
from models.model import Messages, db, migrate, cache
db.init_app(app)
migrate.init_app(app, db)
cache.init_app(app)

# 向app註冊api與routes的藍圖
from api import api
from routes import page
app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(page)


@socketio.on('send_message')
def handle_send_message(data):
	# print('send_message',data)
	r.publish(data["room"], json.dumps(data))
	try:
		message = Messages(scard_id=data["room"], user_id=data["id"], message=data["message"])
		db.session.add(message)
		db.session.commit()
	except:
		db.session.close()
		

msg_p = r.pubsub()
msg_room_lst = []
@socketio.on('join_room')
def handle_join_room(room_id):
	join_room(room_id)
	if room_id not in msg_room_lst:
		msg_p.subscribe(room_id)
	for message in msg_p.listen():
		if isinstance(message.get('data'), bytes):
			msg = json.loads(message['data'])
			msg["time"] = datetime.now().strftime("%-m月%-d日 %H:%M")
			# print(msg, msg["room"])
			emit('receive_message', msg, to=msg["room"])

chan_p = r.pubsub()
chan_lst = []
@socketio.on('sub_channel')
def handle_sub_channel(chan_id):
	join_room(chan_id)
	if chan_id not in chan_lst:
		chan_p.subscribe(chan_id)
	for note in chan_p.listen():
		if isinstance(note.get('data'), bytes):
			msg = json.loads(note['data'])
			# print(type(msg), msg)
			emit('receive_channel', msg, to=msg['channel'])

@socketio.on('unsub_channel')
def handle_unsub_channel(chan_id):
	leave_room(chan_id)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
	socketio.run(app, host="0.0.0.0",port=8000)
