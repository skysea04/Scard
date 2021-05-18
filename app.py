from flask import *

app=Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/signup")
def signup():
	return render_template("signup.html")

@app.route('/basicprofile')
def basicprofile():
    return render_template('basicprofile.html')


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=3000, debug=True)