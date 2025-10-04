import os
import json
import yaml
import random
import subprocess
import importlib
from tempfile import NamedTemporaryFile
from typing import Any
from flask import Flask, render_template, abort, request, redirect, url_for

app = Flask(__name__)

basedir = os.path.dirname(__file__)

problems_path = os.path.join(basedir, 'problems')
statefile_path = os.path.join(basedir, 'user', 'state.json')
configfile_path = os.path.join(basedir, 'user', 'config.yaml')
logfile_path = os.path.join(basedir, 'user', 'log.log')
orderfile_path = os.path.join(basedir, 'user', "order.json")
chrootdir_path = os.path.abspath('debian_filesystem')


with open(configfile_path, 'r') as config_file:
    config_data: dict[str, Any] = yaml.load(config_file, yaml.Loader)
    print(config_data)

    problems: list = config_data['problems']
    teams: list = config_data['teams']
    rooms: dict[str, str] = config_data['rooms']
    unusedRooms: list[str] = config_data['unused-rooms']
    competition_name: str = config_data['competition-name']
    seed: str = config_data['seed']

    uuids = list(rooms.values())
    random.seed(seed)

if os.path.exists(statefile_path):
    with open(statefile_path) as statefile:
        team_state: dict[str, int] = json.loads(statefile.read())
else:
    team_state = {}
    for team in teams:
        team_state[team] = 0
    del team

# Validate team_state
if len(set(team_state.keys())) != len(team_state):
    print(f'File "{statefile_path}" contains duplicate teams')
    exit()
if set(team_state.keys()) != set(teams):
    print(f'File "{statefile_path}" does not contain all teams')
    exit()

def storeState():
    with open(statefile_path, 'w') as statefile:
        statefile.write(json.dumps(team_state, indent=4))


if os.path.exists(orderfile_path):
    with open(orderfile_path) as orderfile:
        team_order: dict[str, list[str]] = json.loads(orderfile.read())
else:
    team_order = {}
    for team in teams:
        team_order.update({team: random.sample(uuids, len(problems))})
    del team

    with open(orderfile_path, 'w') as orderfile:
        orderfile.write(json.dumps(team_order, indent=4))

# Validate team_order
if len(set(team_order.keys())) != len(team_order):
    print(f'File "{orderfile_path}" contains duplicate teams')
    exit()
if set(team_order.keys()) != set(teams):
    print(f'File "{orderfile_path}" does not contain all teams')
    exit()
for order_for_team in team_order.values():
    print(order_for_team)
    for uuid in order_for_team:
        if uuid not in uuids:
            print(f'File "{orderfile_path}" contains uuid "{uuid}" which does associated with a room')
            exit()
if len(set(map(len, team_order.values()))) != 1:
    print(f'File "{orderfile_path}" does not have same number of uuids for all teams')
    exit()
if len(list(team_order.values())[0]) != len(problems):
    print(f'File "{orderfile_path}" does not have same number of uuids as the number of problems in the config')
    exit()


@app.route('/')
def hello():
    if 'team' not in request.cookies:
        return redirect(url_for('login'), code=307)
    elif request.cookies.get('team') not in teams:
        return redirect(url_for('login'), code=307)

    team = request.cookies.get('team')
    problem = problems[team_state[team]]
    if 'problem' in request.args:
        problem = request.args['problem']

    with open(os.path.join(problems_path, problem, 'problem.yaml'), 'r') as problem_file:
        problem_data: dict[str, Any] = yaml.load(problem_file, yaml.Loader)

        problem_type: str = problem_data['type']

    def generateCode():
        problemModule = importlib.import_module(f'problems.{problems[problems.index(problem)]}.generate', package=None)
        roomUuid: str = team_order[team][team_state[team]]
        correctRoom: str = next(room for room in rooms if rooms[room] == roomUuid)
        return problemModule.generateCode(correctRoom, unusedRooms)

    match problem_type:
        case 'pt_what-is-code-doing':
            code = generateCode()
            return render_template('problem.show-code.html',
                                    competitionName=competition_name,
                                    data=problem_data,
                                    code=code)

        case 'pt_text':
            code = generateCode()
            return render_template('problem.show-text.html',
                                    competitionName=competition_name,
                                    data=problem_data,
                                    code=code)

        case 'pass-fail':
            with open(os.path.join(problems_path, problem, 'data', 'sample', '1.in'), 'r') as in_file:
                input_data = in_file.read()
            with open(os.path.join(problems_path, problem, 'data', 'sample', '1.ans'), 'r') as out_file:
                output_data = out_file.read()

            return render_template('problem.submit-code.html',
                                    competitionName=competition_name,
                                    data=problem_data,
                                    input=input_data,
                                    output=output_data)

        case 'pt_input-text':
            return render_template('problem.submit-text.html',
                                    competitionName=competition_name,
                                    data=problem_data)

    return abort(500, 'Unable to parse problem')

@app.route('/login')
def login():
    print(teams)
    return render_template('login.html', competitionName=competition_name, teams=teams)

@app.route('/admin')
def admin():
    return render_template('admin.html',
                           competitionName=competition_name,
                           teams=teams,
                           problems=problems,
                           rooms=rooms,
                           teamState=team_state,
                           teamOrder=team_order)

@app.route('/qr')
def qr():
    team = request.cookies.get('team')
    code_id = request.args.get('id')
    if team not in teams:
        return redirect(f'/login?id={code_id}')

    if not code_id or code_id not in uuids:
        return abort(400, 'Invalid ID')

    # print(f'{team_order[team][team_state[team]] = }')
    print(f'{team = }')
    # print(f'{team_order[team] = }')
    # print(f'{team_state[team] = }')
    print(f'Expected ID: {team_order[team][team_state[team]]}. Code ID: {code_id}')

    if team_order[team][team_state[team]] != code_id:
        return abort(400, 'Fel QR!')

    team_state[team] += 1
    storeState()

    return redirect('/')

@app.route('/api/submit_code', methods=['POST'])
def submit():
    input_data = request.form.get('inputData')
    team = request.cookies.get('team')
    problem_id = request.referrer[-36:]
    problem = problems[team_order[team].index(problem_id)]

    with open(os.path.join(problems_path, problem, f"{problem}.json")) as config_file:
        problem_config_data = json.load(config_file)
        max_time = problem_config_data['max_time']

    shared_test_cases_path = os.path.join(problems_path, problem, 'shared')

    with NamedTemporaryFile(delete=False,
                            dir=os.path.join(chrootdir_path, 'tmp'), suffix='.py') as temp_file:
        host_upload_path = temp_file.name
        jail_upload_path = os.path.join('/tmp', os.path.basename(temp_file.name))
        temp_file.write(input_data.encode())
    os.chmod(host_upload_path, 0o644)

    test_cases = []
    files = sorted(os.listdir(shared_test_cases_path))
    num_cases = len(files) // 2

    for i in range(1, num_cases + 1):
        with open(os.path.join(shared_test_cases_path, f"{i}.in")) as f_in, \
                open(os.path.join(shared_test_cases_path, f"{i}.ans")) as f_ans:
            test_cases.append((f_in.read(), f_ans.read()))

    for input_text, expected_output in test_cases:
        if os.environ.get('AM_I_A_DOCKER_CONTIANER', False):
            command = ["./nsjail"]
        else:
            command = ["sudo", "./nsjail"]

        command.extend([
            "-Mo",
            "-q",
            "--disable_clone_newns",
            "--disable_clone_newuser",
            "--disable_clone_newpid",
            "--disable_clone_newcgroup",
            "--disable_clone_newuts",
            "--disable_clone_newipc",
            "--disable_clone_newnet",
            "--rlimit_cpu", str(max_time),
            "--chroot", chrootdir_path,
            "--",
            "/usr/bin/python3",
            "-u",
            jail_upload_path
        ])

        result = subprocess.run(command,
                                input=input_text,
                                capture_output=True,
                                text=True)

        if result.stdout.strip() != expected_output.strip():
            os.remove(host_upload_path)
            return result.stderr
    # team_state[team] += 1
    # storeState()
    os.remove(host_upload_path)

    return ''.join([name for name, uuid in config_data['rooms'].items() if uuid == team_order[team][team_state[team]]])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969, debug=True)
