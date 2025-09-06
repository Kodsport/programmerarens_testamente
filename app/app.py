from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def hello():
	return "Hello World!"

@app.route('/0a12ef5b-102c-485f-908c-092691d59ce1/')
def clue1():
	return render_template('1/index.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=6969)