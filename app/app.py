import os
import importlib
import json

from flask import Flask, render_template, abort, request, redirect, url_for
app = Flask(__name__)

basedir = os.path.dirname(__file__)

problems_path = os.path.join(basedir, 'problems')
statefile_path = os.path.join(basedir, 'user', 'statefile.json')
configfile_path = os.path.join(basedir, 'user', 'config.json')
logfile_path = os.path.join('user', 'logfile.log')

problems = [p for p in os.listdir(
    problems_path) if os.path.isdir(os.path.join(problems_path, p))]

print('Problems', problems)

with open(configfile_path, 'r') as config_file:
    config_data = json.load(config_file)
    teams = config_data['teams']
    uuids = [config_data['rooms'][i]['uuid']
             for i in range(len(config_data['rooms']))]


# def print(*msg):
#     with open(logfile_path, 'a') as outfile:
#         # outfile.write(f'{msg}\n')
#         try:
#             outfile.write(f'{"".join(map(str, *msg))}\n')
#         except:
#             try:
#                 outfile.write(json.dumps(msg, indent=4))
#             except:
#                 pass


if os.path.exists("statefile_path"):
    with open(statefile_path) as statefile:
        team_state = json.loads(statefile.read())
else:
    team_state = {}
    for team in teams:
        team_state[team] = 0


def storeState():
    global team_state

    with open(statefile_path, 'w') as statefile:
        statefile.write(json.dumps(team_state, indent=4))


@app.route('/')
def hello():
    if 'team' not in request.cookies:
        return redirect(url_for('login'), code=307)
    else:
        return render_template('index.html')


@app.route('/login')
def login():
    print(teams)
    return render_template('login.html', len=len(teams), teams=list(teams))


@app.route('/qr')
def qr():
    id = request.args.get('id')
    team = request.cookies.get('team')
    if team not in teams:
        return redirect('/login')
    if not id or id not in uuids:
        return abort(400, 'Invalid ID')
    print(f'{id=}, {team=}, {team[team_state[team]]=}')

    if team[team_state[team]] == id:
        team_state[team] += 1
        storeState()
    if team_state[team] > 0 and team[team_state[team]-1] == id:
        pass
    else:
        return abort(401, 'Fel QR')

    problem = problems[team_state[team]]

    print(f'{problem=}')

    return render_template('problem.html', problem=problem)


@app.route('/problem')
def problem():
    problem = request.args.get('problem')
    if not problem or problem not in problems:
        abort(400, 'Invalid ID')
    id = request.args.get('id')
    if not id or id not in uuids:
        return abort(400, 'Invalid ID')
    flag = uuids[id]
    print(f'{problem=}')
    problemModule = importlib.import_module(
        f'problem.{problems[problems.index(problem)]}', package=None)
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
