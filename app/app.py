from uuids import uuids
from teams import teams
import os
import importlib
import json

from flask import Flask, render_template, abort, request, redirect, url_for
app = Flask(__name__)

basedir = os.path.dirname(__file__)
problems = list(map(lambda filename: filename.removesuffix('.py'), filter(lambda filename: filename.endswith('.py') and filename != 'template.py', os.listdir(os.path.join(basedir, 'problem')))))

statefilePath = os.path.join(basedir, 'statefile.json')

print('Problems', problems)

if os.path.exists(statefilePath):
	with open(statefilePath) as statefile:
		STATE = json.loads(statefile.read())
else:
	STATE = {
		'team-a': 1
	}

def storeState():
	global STATE

	with open(statefilePath, 'w') as statefile:
		STATE = json.loads(statefile.read())

@app.route('/')
def hello():
	if 'team' not in request.cookies:
		return redirect(url_for('login'), code=307)
	else:
		return render_template('index.html')

@app.route('/login')
def login():
	return render_template('login.html', len = len(teams), teams = teams)

@app.route('/qr')
def qr():
	id = request.args.get('id')
	if not id or id not in uuids: return abort(400, 'Invalid ID')
	print(f'{id=}')
	return render_template('problem.html', uuid=uuids[id])

@app.route('/problem')
def problem():
	problem = request.args.get('problem')
	if not problem or problem not in problems: abort(400, 'Invalid ID')
	print(f'{problem=}')
	problemModule = importlib.import_module(f'problem.{problems[problems.index(problem)]}', package=None)
	if getattr(problemModule, 'generateFile', None):
		return render_template('problem.html', filename=problem)
	elif getattr(problemModule, 'generateText', None):
		return render_template('problem.html', text=problemModule.generateText('heje'))
	elif getattr(problemModule, 'generateImage', None):
		return render_template('problem.html', image='image')
	else:
		return abort(500, 'Invalid problem')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=6969)
