from uppgifter import uppgifter

from flask import Flask, render_template, abort, request
app = Flask(__name__)

@app.route('/')
def hello():
	return "Hello World!"

@app.route('/qr')
def qr():
	id = request.args.get('id')
	if not id or id not in uppgifter: abort(400, 'Invalid ID')
	print(f'{id=}')
	return render_template('qr.html', uppgift=uppgifter[id])

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=6969)
