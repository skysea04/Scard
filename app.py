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


'''test area'''
# import smtplib
# mail_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
# mail_server.login(mail_username, mail_password)
# import email.message
'''test area'''




app = Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:3306/{mysql_database}?charset=utf8mb4'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping":True}


socketio = SocketIO(app)
from models.model import Messages, Post, PostBoard, User, db, migrate, cache
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
	try:
		boards = PostBoard.query.all()
		board_list = []
		for post_board in boards:
			board_list.append(post_board.sys_name)
		if board == None or board in board_list:
			return render_template('index.html')
	except:
		abort(500)


@app.route('/b/<board>/p/<post_id>')
def view_post(board, post_id):
	try:
		post = Post.query.filter_by(id=post_id).first()
		if post:
			right_board = PostBoard.view_board(post.board_id)
			if right_board.sys_name == board:
				return render_template('post.html')
			else:
				return redirect(f'/b/{right_board.sys_name}/p/{post_id}')
		else:
			return render_template('post-not-exist.html')
	except:
		abort(500)

@app.route('/b/<board>/p/<post_id>/edit')
def edit_post(board, post_id):
	try:
		if 'user' in session:
			user_id = session['user']['id']
			post = Post.query.filter_by(id=post_id).first()
			if post:
				if post.user_id == user_id:
					return render_template('patch-post.html')
			else:
				return render_template('post-not-exist.html')
		return redirect(f'/b/{board}/p/{post_id}')
	except:
		abort(500)
			

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

@app.route('/mailverify')
def go_to_verify_mail():
	if 'user' in session:
		verify = session['user']['verify_status']
		if verify == 'stranger':
			user_email = session['user']['email']
			return render_template('verify-my-mail.html',mail=user_email)
	return redirect(url_for('show_board'))
		

@app.route('/mailverify/<email>')
def mail_verify(email):
	try:
		user = User.query.filter_by(email=email).first()
		if not user:
			abort(404)
		if user.verify_status == 'stranger':
			user.verify_status = 'mail'
			session["user"] = False
			session["user"] = {
				"id": user.id,
				"verify_status": user.verify_status,
				"collage": user.collage,
				"department": user.department,
				"commentAvatar": user.comment_avatar
			}
			db.session.commit()
		return render_template('mail-verified.html')
	except:
		abort(500)

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
	try: 
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
	except:
		abort(500)

@app.route('/message/<id>')
def message(id):
	if 'user' in session:
		return render_template('message.html')
	return redirect(url_for('signup'))


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
	socketio.run(app, host="0.0.0.0",port=8000, debug=True)
