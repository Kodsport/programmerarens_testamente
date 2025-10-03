import os
import json
import random

from flask import Flask, render_template, abort, request, redirect, url_for
app = Flask(__name__)

basedir = os.path.dirname(__file__)

problems_path = os.path.join(basedir, 'problems')
attempts_path = os.path.join(basedir, 'user', 'attempts')
statefile_path = os.path.join(basedir, 'user', 'statefile.json')
configfile_path = os.path.join(basedir, 'user', 'config.json')
logfile_path = os.path.join(basedir, 'user', 'logfile.log')
orderfile_path = os.path.join(basedir, 'user', "order.json")


with open(configfile_path, 'r') as config_file:
    config_data = json.load(config_file)
    problems = config_data['problems']
    teams = config_data['teams']
    uuids = [config_data['rooms'][i]['uuid']
             for i in range(len(config_data['rooms']))]


if os.path.exists(statefile_path):
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


random.seed(config_data['seed'])

if os.path.exists(orderfile_path):
    with open(orderfile_path) as orderfile:
        team_order = json.loads(orderfile.read())
else:
    team_order = {}
    for team in teams:
        team_order.update({team: random.sample(uuids, len(uuids))})

    with open(orderfile_path, 'w') as orderfile:
        orderfile.write(json.dumps(team_order, indent=4))


@app.route('/')
def hello():
    if 'team' not in request.cookies:
        return redirect(url_for('login'), code=307)
    elif request.cookies.get('team') not in teams:
        return redirect(url_for('login'), code=307)
    else:
        return render_template('index.html')


@app.route('/login')
def login():
    print(teams)
    return render_template('login.html', len=len(teams), teams=list(teams))


@app.route('/qr')
def qr():
    team = request.cookies.get('team')
    problem_id = request.args.get('id')
    if team not in teams:
        return redirect('/login')
    problem = problems[team_state[team]]

    if not problem_id or problem_id not in uuids:
        return abort(400, 'Invalid ID')
    if team_order[team][team_state[team]] != problem_id:
        return render_template('error.html', error='Fel QR!'), 404

    with open(f"{problems_path}/{problem}/{problem}.json", 'r') as problem_file:
        problem_data = json.load(problem_file)
        problem_name = problem_data['name']
        problem_desc = problem_data['description']

    return render_template('problem.html', name=problem_name, description=problem_desc)


@app.route('/api/submit', methods=['POST'])
def submit():
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969)
