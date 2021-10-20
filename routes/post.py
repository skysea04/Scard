from flask import  session, redirect, url_for, render_template, abort
from . import page, Post, PostBoard
@page.route('/')
def index():
	return redirect('/b')

@page.route('/b')
@page.route('/b/<board>')
def show_board(board=None):
	try:
		boards = PostBoard.query.all()
		board_list = []
		for post_board in boards:
			board_list.append(post_board.id)
		if board == None or board in board_list:
			return render_template('index.html')
	except:
		abort(500)


@page.route('/b/<board>/p/<post_id>')
def view_post(board, post_id):
	try:
		post = Post.query.filter_by(id=post_id).first()
		if post:
			# right_board = PostBoard.view_board(post.board_id)
			if post.board_id == board:
				return render_template('post.html')
			else:
				return redirect(f'/b/{post.board_id}/p/{post_id}')
		else:
			return render_template('post-not-exist.html')
	except:
		abort(500)

@page.route('/b/<board>/p/<post_id>/edit')
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
			

@page.route('/new-post')
def new_post():
	if 'user' in session:
		return render_template('new-post.html')
	return redirect(url_for('page.signup'))
