from uuids import uuids
from teams import teams
import os
import importlib
import json

from flask import Flask, render_template, abort, request, redirect, url_for
app = Flask(__name__)

basedir = os.path.dirname(__file__)
problems = list(map(lambda filename: filename.removesuffix('.py'), filter(lambda filename: filename.endswith('.py') and filename != 'template.py', os.listdir(os.path.join(basedir, 'problem')))))

statefilePath = os.path.join(basedir, 'user', 'statefile.json')

print('Problems', problems)

logfilepath = os.path.join('user', 'logfile.log')

def print(*msg):
	with open(logfilepath, 'a') as outfile:
		# outfile.write(f'{msg}\n')
		outfile.write(f'{" ".join(msg)}\n')

if os.path.exists(statefilePath):
	with open(statefilePath) as statefile:
		STATE = json.loads(statefile.read())
else:
	STATE = {
		'team-int': 0,
		'team-float': 0,
		'team-str': 0,
		'team-bool': 0,
		'team-None': 0,
	}

def storeState():
	global STATE

	with open(statefilePath, 'w') as statefile:
		statefile.write(json.dumps(STATE, indent=4))

@app.route('/')
def hello():
	if 'team' not in request.cookies:
		return redirect(url_for('login'), code=307)
	else:
		return render_template('index.html')

@app.route('/login')
def login():
	print(teams, teams.keys())
	return render_template('login.html', len = len(teams), teams = list(teams.keys()))

@app.route('/qr')
def qr():
	id = request.args.get('id')
	team = request.cookies.get('team')
	if not team in teams: return redirect('/login')
	if not id or id not in uuids: return abort(400, 'Invalid ID')
	print(f'{id=}, {team=}, {teams[team][STATE[f"team-{team}"]]=}')

	if teams[team][STATE[f'team-{team}']] == id:
		STATE[f'team-{team}'] += 1
		storeState()
	if STATE[f'team-{team}'] > 0 and teams[team][STATE[f'team-{team}']-1] == id:
		pass
	else:
		return abort(401, 'Fel QR')

	problem = problems[STATE[f'team-{team}']]

	flag = uuids[teams[team][STATE[f'team-{team}']]]

	print(f'{problem=}')
	problemModule = importlib.import_module(f'problem.{problems[problems.index(problem)]}', package=None)
	if getattr(problemModule, 'generateFile', None):
		return render_template('problem.html', text=problemModule.generateFile(problems[STATE[f'team-{team}']]))
	elif getattr(problemModule, 'generateText', None):
		return render_template('problem.html', text=problemModule.generateText(flag))
	elif getattr(problemModule, 'generateImage', None):
		return render_template('problem.html', image='image')
	else:
		return abort(500, 'Invalid problem')

@app.route('/problem')
def problem():
	problem = request.args.get('problem')
	if not problem or problem not in problems: abort(400, 'Invalid ID')
	id = request.args.get('id')
	if not id or id not in uuids: return abort(400, 'Invalid ID')
	flag = uuids[id]
	print(f'{problem=}')
	problemModule = importlib.import_module(f'problem.{problems[problems.index(problem)]}', package=None)
	if getattr(problemModule, 'generateFile', None):
		return render_template('problem.html', filename=problem)
	elif getattr(problemModule, 'generateText', None):
		return render_template('problem.html', text=problemModule.generateText(flag))
	elif getattr(problemModule, 'generateImage', None):
		return render_template('problem.html', image='image')
	else:
		return abort(500, 'Invalid problem')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=6969)
