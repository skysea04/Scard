from flask import  session, redirect, url_for, render_template, abort
from . import page, db, User
@page.route('/signup')
def signup():
	if 'user' in session:
		return redirect(url_for('page.show_board'))
	return render_template('signup.html')

@page.route('/mailverify')
def go_to_verify_mail():
	if 'user' in session:
		verify = session['user']['verify_status']
		if verify == 'stranger':
			user_email = session['user']['email']
			return render_template('verify-my-mail.html',mail=user_email)
	return redirect(url_for('page.show_board'))
		

@page.route('/mailverify/<email>')
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

@page.route('/basicprofile')
def basic_profile():
	if 'user' in session:
		return render_template('basic-profile.html')
	return redirect(url_for('page.signup'))

@page.route('/my/profile')
def my_profile():
	if 'user' in session:
		return render_template('my-profile.html')
	return redirect(url_for('page.signup'))