from uuids import uuids

from flask import Flask, render_template, abort, request
app = Flask(__name__)

teams = ["a", "b", "c"]

@app.route('/')
def hello():
	return "Hello World!"

@app.route('/login')
def login():
	return render_template('login.html', len = len(teams), teams = teams)


@app.route('/qr')
def qr():
	id = request.args.get('id')
	if not id or id not in uuids: abort(400, 'Invalid ID')
	print(f'{id=}')
	return render_template('qr.html', uuid=uuids[id])

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=6969)
