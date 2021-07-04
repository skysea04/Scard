from logging import debug
from flask import *
from flask_socketio import SocketIO, join_room, send, emit
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_host = os.getenv("MYSQL_HOST")
mysql_database = os.getenv("MYSQL_DATABASE")
redis_host = os.getenv("REDIS_HOST")
'''test area'''
from redis import Redis
r = Redis(host=redis_host, port=6379)
'''test area'''




app = Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:3306/{mysql_database}'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping":True}

socketio = SocketIO(app)
from models.model import Messages, Post, PostBoard, db, migrate, cache
db.init_app(app)
migrate.init_app(app, db)

cache.init_app(app)

# 向app註冊api的藍圖
from api import api
app.register_blueprint(api, url_prefix="/api")

@app.route('/')
def index():
	return redirect(url_for('show_board'))

@app.route('/b')
@app.route('/b/<board>')
def show_board(board=None):
	boards = PostBoard.query.all()
	board_list = []
	for post_board in boards:
		board_list.append(post_board.sys_name)
	if board == None or board in board_list:
		return render_template('index.html')
	abort(404)

@app.route('/b/<board>/p/<post_id>')
def view_post(board, post_id):
	post = Post.query.filter_by(id=post_id).first()
	if post:
		right_board = PostBoard.view_board(post.board_id)
		if right_board.sys_name == board:
			return render_template('post.html')
		else:
			return redirect(f'/b/{right_board.sys_name}/p/{post_id}')
	else:
		return render_template('post-not-exist.html')
			

@app.route('/new-post')
def new_post():
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
		message_id = db.session.execute("SELECT messages.scard_id\
		FROM messages INNER JOIN scard ON messages.scard_id = scard.id\
		WHERE scard.user_1 = :id or scard.user_2 = :id\
		ORDER BY messages.id DESC\
		LIMIT 1", {"id":user_id}).first()
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

# @socketio.on('message')
# def handle_message(msg):
#     print('get message:'+ msg)
#     send(msg, broadcast=True)

# @socketio.on('join_room')
# def handle_join_room(room_id):
# 	join_room(room_id)
# 	# send(room_id)

# @socketio.on('send_message')
# def handle_send_message(data):
# 	data["time"] = datetime.now().strftime("%-m月%-d日 %H:%M")
# 	socketio.emit('receive_message', data, room=data["room"])
# 	message = Messages(scard_id=data["room"], user_id=data["id"], message=data["message"])
# 	db.session.add(message)
# 	db.session.commit()

@socketio.on('send_message')
def handle_send_message(data):
	# print('send_message',data)
	r.publish(data["room"], json.dumps(data))
	message = Messages(scard_id=data["room"], user_id=data["id"], message=data["message"])
	db.session.add(message)
	db.session.commit()

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
			print(msg, msg["room"])
			emit('receive_message', msg, to=msg["room"])

post_p = r.pubsub()
post_room_lst = []
@socketio.on('follow_post')
def handle_follow_post(post_id):
	print('link', post_id)
	post_room = f'post{post_id}'
	join_room(post_room)
	if post_room not in post_room_lst:
		post_p.subscribe(post_room)
	for note in post_p.listen():
		# print('listen')
		if isinstance(note.get('data'), bytes):
			msg = json.loads(note['data'])
			# msg["time"] = datetime.now().strftime("%-m月%-d日 %H:%M")
			# print(type(msg), msg)
			emit('receive_post_note', msg, to=msg['room'])

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

if __name__ == '__main__':
	socketio.run(app, host="0.0.0.0",port=8000, debug=True)
