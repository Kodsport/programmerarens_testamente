import os
import json
import yaml
import random
import subprocess
import importlib
import logging
from tempfile import NamedTemporaryFile
from typing import Any
from flask import Flask, render_template, url_for, abort, redirect, request, make_response

logger = logging.getLogger(__name__)

app = Flask(__name__)

basedir = os.path.dirname(__file__)

problems_path = os.path.join(basedir, 'problems')
statefile_path = os.path.join(basedir, 'user', 'state.json')
configfile_path = os.path.join(basedir, 'user', 'config.yaml')
logfile_path = os.path.join(basedir, 'user', 'log.log')
chrootdir_path = os.path.abspath('debian_filesystem')

logging.basicConfig(filename=logfile_path, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())

with open(configfile_path, 'r') as config_file:
    config_data: dict[str, Any] = yaml.load(config_file, yaml.Loader)
    logger.info(f'{config_data=}')

    seed: str = config_data['seed']
    competition_name: str = config_data['competition-name']
    admin_password: str = config_data['admin-password']
    teams: list = config_data['teams']
    rooms: dict[str, str] = config_data['rooms']
    final_room: dict[str] = config_data['final-room']
    unused_rooms: list[str] = config_data['unused-rooms']
    problems: list = config_data['problems']
    override_nsjail: bool = config_data['override-nsjail'] if 'override-nsjail' in config_data else False

    random.seed(seed)

    if len(rooms.keys()) < (len(problems) - 1):
        logging.critical(
            'There must be at least as many rooms as there are problems')
        exit(1)

    team_order = {}
    for team in teams:
        team_order.update({team: random.sample(list(rooms.values()), len(
            problems) - 1) + [list(final_room.values())[0]]})
    del team

    rooms[list(final_room.keys())[0]] = list(final_room.values())[0]

    uuids = list(rooms.values())

if not isinstance(competition_name, str):
    logging.critical('Config entry "competition-name" must be of type string')
    exit(1)
if not isinstance(teams, list):
    logging.critical('Config entry "teams" must be list of type list')
    exit(1)
if len(teams) <= 0:
    logging.critical('Config entry "teams" contain at least one element')
    exit(1)
if any([not isinstance(team, str) for team in teams]):
    logging.critical('Config entry "teams" elements must be of type string')
    exit(1)
if len(set(rooms.keys())) != len(rooms):
    logging.critical('Config entry "rooms" must have unique room names')
    exit(1)
if len(set(rooms.values())) != len(rooms):
    logging.critical('Config entry "rooms" must have unique uuids')
    exit(1)
if len(set(rooms.keys()).intersection(set(unused_rooms))) > 0:
    logging.critical(
        'Config entry "unused_rooms" must only contain unused rooms')
    exit(1)
if len(final_room) != 1:
    logging.critical('Config entry "final_room" must contain exactly one room')
    exit(1)
if len(set(unused_rooms)) != len(unused_rooms):
    logging.critical('Config entry "unused_rooms" must have unique room names')
    exit(1)
if len(set(problems)) != len(problems):
    logging.critical('Config entry "problems" must have unique problems')
    exit(1)

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
    logger.critical(f'File "{statefile_path}" contains duplicate teams')
    exit(1)
if set(team_state.keys()) != set(teams):
    logger.critical(f'File "{statefile_path}" does not contain all teams')
    exit(1)


def storeState():
    with open(statefile_path, 'w') as statefile:
        statefile.write(json.dumps(team_state, indent=4))


def isAdmin():
    if not admin_password: return True

    userAuth = request.authorization
    logger.info(f'Admin access: {userAuth = }')

    if not userAuth:
        return False
    if userAuth.type != 'basic':
        return False
    if userAuth.parameters.get('password', '') != admin_password:
        return False
    return True

@app.route('/admin')
def admin():
    if not isAdmin():
        resp = make_response()
        resp.headers.add('WWW-Authenticate', 'Basic realm="Admin login"')
        resp.status_code = 401
        return resp

    return render_template('admin.html',
                           competitionName=competition_name,
                           teams=teams,
                           problems=problems,
                           rooms=rooms,
                           teamState=team_state,
                           teamOrder=team_order,
                           hasAuth=bool(admin_password))

@app.route('/admin/logout')
def admin_logout():
    resp = make_response()
    resp.headers.add('WWW-Authenticate', 'Basic realm="Admin login"')
    resp.status_code = 401
    resp.data = '<a href="/admin">admin</a>'
    return resp

@app.route('/')
def hello():
    if 'team' not in request.cookies:
        return redirect(url_for('login'), code=307)
    elif request.cookies.get('team') not in teams:
        return redirect(url_for('login'), code=307)

    team = request.cookies.get('team')

    if (team_state[team] >= len(problems)):
        return 'Slut'

    problem = problems[team_state[team]]
    if isAdmin() and 'problem' in request.args:
        problem = request.args['problem']

    with open(os.path.join(
            problems_path, problem, 'problem.yaml'), 'r') as problem_file:
        problem_data: dict[str, Any] = yaml.load(problem_file, yaml.Loader)

        problem_type: str = problem_data['type']

    def generateCode():
        problemModule = importlib.import_module(
            f'problems.{problems[problems.index(problem)]}.generate',
            package=None)
        roomUuid: str = team_order[team][team_state[team]]
        correctRoom: str = next(
            room for room in rooms if rooms[room] == roomUuid)
        return problemModule.generateCode(correctRoom, unused_rooms)

    match problem_type:
        case 'pt_what-is-code-doing':
            code = generateCode()
            return render_template('problem.show-code.html',
                                   competitionName=competition_name,
                                   team=team,
                                   problem=problem,
                                   data=problem_data,
                                   code=code)

        case 'pt_text':
            code = generateCode()
            return render_template('problem.show-text.html',
                                   competitionName=competition_name,
                                   team=team,
                                   problem=problem,
                                   data=problem_data,
                                   code=code)

        case 'pass-fail':
            test_cases = set([file.split('.')[0] for file in os.listdir(
                os.path.join(problems_path, problem, 'data', 'sample'))])
            samples: list[tuple[str, str]] = []
            for test_case in test_cases:
                with open(os.path.join(
                    problems_path, problem, 'data', 'sample',
                        f'{test_case}.in'), 'r') as in_file, \
                        open(os.path.join(
                            problems_path, problem, 'data', 'sample',
                            f'{test_case}.ans'), 'r') as out_file:
                    samples.append((in_file.read(), out_file.read()))

            return render_template('problem.submit-code.html',
                                   competitionName=competition_name,
                                   team=team,
                                   problem=problem,
                                   data=problem_data,
                                   samples=samples)

        case 'pt_input-text':
            return render_template('problem.submit-text.html',
                                   competitionName=competition_name,
                                   team=team,
                                   problem=problem,
                                   data=problem_data)

    logger.error(f'Unknown problem type: {problem_type=}')

    return abort(500, 'Unable to parse problem')


@app.route('/login')
def login():
    logger.debug(teams)
    return render_template('login.html', competitionName=competition_name,
                           teams=teams)

@app.route('/qr')
def qr():
    team = request.cookies.get('team')
    code_id = request.args.get('id')
    if team not in teams:
        return redirect(f'/login?id={code_id}')

    if not code_id or code_id not in uuids:
        return abort(400, 'Invalid ID')

    # logger.debug(f'{team_order[team][team_state[team]] = }')
    logger.debug(f'{team=}')
    # logger.debug(f'{team_order[team] = }')
    # logger.debug(f'{team_state[team] = }')
    logger.debug(
        f'Expected ID: {team_order[team][team_state[team]]}\
        . Code ID: {code_id}')

    if team_order[team][team_state[team]] != code_id:
        return abort(400, 'Fel QR!')

    team_state[team] += 1
    storeState()

    return redirect('/')


def test_file(file_data, test_cases: list[tuple[str, str]], max_time: int):
    if not test_cases:
        return True

    if not override_nsjail:
        with NamedTemporaryFile(delete=False,
                                dir=os.path.join(chrootdir_path, 'tmp'),
                                suffix='.py') as temp_file:
            host_upload_path = temp_file.name
            jail_upload_path = os.path.join(
                '/tmp', os.path.basename(temp_file.name))
            temp_file.write(file_data.encode())
        os.chmod(host_upload_path, 0o644)

        for input_text, expected_output in test_cases:
            if os.environ.get('AM_I_A_DOCKER_CONTIANER', False):
                command = ['./nsjail']
            else:
                command = ['sudo', './nsjail']

            command.extend([
                '-Mo',
                '-q',
                '--disable_clone_newns',
                '--disable_clone_newuser',
                '--disable_clone_newpid',
                '--disable_clone_newcgroup',
                '--disable_clone_newuts',
                '--disable_clone_newipc',
                '--disable_clone_newnet',
                '--rlimit_cpu', str(max_time),
                '--chroot', chrootdir_path,
                '--',
                '/usr/bin/python3',
                '-u',
                jail_upload_path
            ])

            result = subprocess.run(command,
                                    input=input_text,
                                    capture_output=True,
                                    text=True)

            if result.returncode != 0:
                return False

            if result.stdout.strip() != expected_output.strip():
                return False
        os.remove(host_upload_path)
        return True
    else:
        logger.debug(f'{file_data=}')
        logger.debug(f'{test_cases=}')
        logger.debug(f'{max_time=}')
        import time
        time.sleep(random.random() * max_time)
        # Just pretend to do test
        return random.choice([True, False])


@app.route('/api/submit_code', methods=['POST'])
def submit():
    input_data = request.form.get('inputData')
    if not input_data:
        return json.dumps(('error', 'No file input!')), 400

    team = request.cookies.get('team')
    if team_state[team] >= len(problems):
        return json.dumps(
            ('error', 'No more problems available for this team')), 400

    problem = problems[team_state[team]]

    with open(os.path.join(
            problems_path, problem, 'problem.yaml')) as config_file:
        problem_config_data = yaml.load(config_file, yaml.Loader)

        problem_type: str = problem_config_data['type']

    for name, uuid in rooms.items():
        if uuid == team_order[team][team_state[team]]:
            next_room = ''.join(name)

    match problem_type:
        case 'pass-fail':
            try:
                max_time: int = problem_config_data['max_time']
            except KeyError:
                max_time: int = 5

            sample_test_cases_path = os.path.join(
                problems_path, problem, 'data', 'sample')
            secret_test_cases_path = os.path.join(
                problems_path, problem, 'data', 'secret')

            sample_test_cases: list[tuple[str, str]] = []
            for i in range(int(len(os.listdir(sample_test_cases_path))/2)):
                with open(
                    os.path.join(sample_test_cases_path,
                                f'{i+1}.in')) as f_in, \
                        open(
                            os.path.join(sample_test_cases_path,
                                        f'{i+1}.ans')) as f_ans:
                    sample_test_cases.append((f_in.read(), f_ans.read()))

            passes_sample = test_file(input_data, sample_test_cases, max_time)

            secret_test_cases: list[tuple[str, str]] = []
            if os.path.exists(secret_test_cases_path):
                for i in range(int(len(os.listdir(secret_test_cases_path))/2)):
                    with open(
                        os.path.join(secret_test_cases_path,
                                    f'{i+1}.in')) as f_in, \
                            open(
                            os.path.join(secret_test_cases_path,
                                        f'{i+1}.ans')) as f_ans:
                        secret_test_cases.append((f_in.read(), f_ans.read()))

            passes_secret = test_file(input_data, secret_test_cases, max_time)

            if passes_sample is True and passes_secret is True:
                return json.dumps({
                    'room': next_room,
                    'sample': passes_sample,
                    'secret': passes_secret
                })
            else:
                return json.dumps({
                    'sample': passes_sample,
                    'secret': passes_secret
                })

        case 'pt_input-text':
            correct = [option.strip().lower() for option in problem_config_data['correct']]
            if input_data.strip().lower() in correct:
                return json.dumps({
                    'room': next_room
                })
            return json.dumps({
                'error': 'incorrect'
            })

    logger.error(f'Unknown problem type: {problem_type=}')

    return abort(500, 'Unable to parse problem')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969, debug=True)
