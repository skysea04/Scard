from flask import  session, redirect, url_for, render_template, abort
from . import page, db

@page.route('/scard')
def scard():
	if 'user' in session:
		return render_template('scard.html')
	return redirect(url_for('page.signup'))

@page.route('/message')
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
				return redirect(url_for('page.message', id=message_id))
		return redirect('/b')
	except:
		abort(500)

@page.route('/message/<id>')
def message(id):
	if 'user' in session:
		return render_template('message.html')
	return redirect(url_for('page.signup'))