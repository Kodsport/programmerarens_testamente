import os
import json
import random
import subprocess
from tempfile import NamedTemporaryFile

from flask import Flask, render_template, abort, request, redirect, url_for
app = Flask(__name__)

basedir = os.path.dirname(__file__)

problems_path = os.path.join(basedir, 'problems')
statefile_path = os.path.join(basedir, 'user', 'statefile.json')
configfile_path = os.path.join(basedir, 'user', 'config.json')
logfile_path = os.path.join(basedir, 'user', 'logfile.log')
orderfile_path = os.path.join(basedir, 'user', "order.json")
chrootdir_path = os.path.abspath('debian_filesystem')


with open(configfile_path, 'r') as config_file:
    config_data = json.load(config_file)
    problems = config_data['problems']
    teams = config_data['teams']
    uuids = list(config_data['rooms'].values())


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

    with open(os.path.join(problems_path, problem, f"{problem}.json"), 'r') as problem_file:
        problem_data = json.load(problem_file)
        problem_name = problem_data['name']
        problem_desc = problem_data['description']

    return render_template('problem.html', name=problem_name, description=problem_desc)


@app.route('/api/submit', methods=['POST'])
def submit():
    input_data = request.form.get('inputData')
    team = request.cookies.get('team')
    problem_id = request.referrer[-36:]
    problem = problems[team_order[team].index(problem_id)]
    shared_test_cases_path = os.path.join(problems_path, problem, 'shared')

    with NamedTemporaryFile(delete=False,
                            dir=os.path.join(chrootdir_path, 'tmp'), suffix='.py') as temp_file:
        upload_path = temp_file.name
        temp_file.write(input_data.encode())

    test_cases = {}
    for i in range(int(len(os.listdir(shared_test_cases_path))/2)):
        with open(os.path.join(shared_test_cases_path, f"{i+1}.in")) as in_data, open(os.path.join(shared_test_cases_path, f"{i+1}.ans")) as response:
            test_cases[in_data.read()] = response.read()

        command = f"sudo ./nsjail -Mo -Q --chroot {chrootdir_path} -- /usr/bin/echo {list(test_cases.keys())[i]} | /usr/bin/python3 {upload_path}"  # Remove sudo when running docker container
        output = subprocess.run(command, capture_output=True, text=True, shell=True)
        if output.stdout.strip() != list(test_cases.values())[i].strip():
            os.remove(upload_path)
            return output.stderr
    # team_state[team] += 1
    # storeState()
    os.remove(upload_path)
    print(config_data['rooms'])
    return ''.join([name for name, uuid in config_data['rooms'].items() if uuid == team_order[team][team_state[team]]])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969)
