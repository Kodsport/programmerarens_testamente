import os
import json
import random

from flask import Flask, render_template, abort, request, redirect, url_for
app = Flask(__name__)

basedir = os.path.dirname(__file__)

problems_path = os.path.join(basedir, 'problems')
attempts_path = os.path.join(basedir, 'user', 'solutions')
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
    problem_id = request.args.get('id')
    team = request.cookies.get('team')
    problem = problems[team_state[team]]

    if team not in teams:
        return redirect('/login')
    if not problem_id or problem_id not in uuids:
        return abort(400, 'Invalid ID')
    if team_order[team][team_state[team]] != problem_id:
        return render_template('qr-error.html'), 404

    with open(f"{problems_path}/{problem}/{problem}.json", 'r') as problem_file:
        problem_data = json.load(problem_file)
        problem_name = problem_data['name']
        problem_desc = problem_data['description']

    return render_template('problem.html', name=problem_name, description=problem_desc)


@app.route('/api/submit', methods=['POST'])
def submit():
    input_data = request.form.get('inputData')
    referrer = request.headers.get('Referer')
    problem_id = referrer[-36:]
    team = request.cookies.get('team')
    team_attempts_path = os.path.join(attempts_path, team)

    if not os.path.exists(team_attempts_path):
        os.mkdir(team_attempts_path)

    existing_attempts = []
    for file in os.listdir(team_attempts_path):
        if os.path.isfile(os.path.join(team_attempts_path, file)):
            existing_attempts.append(file)

    attempts = {}
    for problem in problems:
        temp = []
        for file_name in existing_attempts:
            if file_name.split('.')[0] == problem:
                temp.append(int(file_name.split('.')[1]))
        try:
            number_of_attempts = max(temp)
        except ValueError:
            number_of_attempts = 0
        attempts.update({problem: number_of_attempts})

    problem_name = problems[team_order[team].index(problem_id)]
    file_name = f"{problem_name}.{attempts[problem_name]+1}.py"
    file_path = os.path.join(team_attempts_path, file_name)
    with open(file_path, 'w') as file:
        file.write(input_data)

    return attempts, 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969)
