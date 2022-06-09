from flask import Blueprint, request, jsonify

from app.Status import Status
from app.models import Change, Incident, Problem, SoftwareConfiguration, HardwareConfiguration, SLAConfiguration, User, ProblemComment, IncidentComment, db

routes_bp = Blueprint('routes', __name__, )


@routes_bp.route('/', methods=['GET'])
def index():
    return 'Hola'

# Configuration

# Changes

@routes_bp.route('/change', methods=['GET'])
def getChanges():
    return jsonify(list(map(changeToDict, Change.query.all())))

@routes_bp.route('/change/<id>', methods=['GET'])
def getChangeById(id):
    return jsonify(changeToDict(Change.query.get(id)))

@routes_bp.route('/problem', methods=['POST'])
def postChange():
    content = request.json
    if not 'name' in content or 'problem_id' not in content:
        return getError('Faltan atributos obligatorios para un cambio.')

    change = Change(name=content['name'], problem_id=content['problem_id'])

    if 'description' in content:
        change.description = content['description']

    if 'proprity' in content:
        change.priority = content['priority']

    if 'proprity' in content:
        change.priority = content['priority']

    if 'created_by_id' in content:
        change.created_by_id = content['created_by_id']

    if 'change_id' in content:
        change.change_id = content['change_id']

    db.session.add(change)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "id": change.id
    })

def changeToDict(change):
    return {
        'id': change.id,
        'description' : change.description,
        'created_by_id': change.created_by_id,
        'priority': change.priority,
        'name': change.name,
        'problem_id' : change.problem_id
    }

# Problems

@routes_bp.route('/problem/<id>/comment', methods=['GET'])
def getProblemComments(problem_id):
    comments = ProblemComment.query.filter_by(problem_id=problem_id)
    return jsonify(list(map(lambda x: x.comment, comments)))

@routes_bp.route('/problem/<id>/comment', methods=['POST'])
def commentProblem(problem_id):
    content = request.json
    if not 'comment' in content:
        return getError('Falta el comentario.')

    comment = ProblemComment(comment=content['comment'], problem_id=problem_id)

    db.session.add(comment)
    db.session.commit()

@routes_bp.route('/problem', methods=['GET'])
def getProblems():
    return jsonify(list(map(problemToDict, Problem.query.all())))

@routes_bp.route('/problem/<id>', methods=['GET'])
def getProblemById(id):
    return jsonify(problemToDict(Problem.query.get(id)))

@routes_bp.route('/problem/<id>/take', methods=['POST'])
def takeProblem(problem_id):
    content = request.json
    if not 'taken_by_id' in content:
        return getError('Falta el ID del usuario.')

    incidents = Incident.query.filter_by(problem_id=problem_id)
    for incident in incidents:
        incident.status = Status.TAKEN

    problem = Problem.query.get(problem_id)
    problem.taken_by_id = content['taken_by_id']
    problem.status = Status.TAKEN
    db.session.commit()

@routes_bp.route('/problem/<id>/solve', methods=['POST'])
def solveProblem(problem_id):
    problem = Problem.query.get(problem_id)
    problem.status = Status.SOLVED

    incidents = Incident.query.filter_by(problem_id=problem_id)
    for incident in incidents:
        incident.status = Status.SOLVED

    db.session.commit()

@routes_bp.route('/problem', methods=['POST'])
def postProblem():
    content = request.json
    if not 'name' in content:
        return getError('Faltan atributos obligatorios para un problema.')

    problem = Problem(name=content['name'], status=Status.CREATED)

    if 'proprity' in content:
        problem.priority = content['priority']

    if 'created_by_id' in content:
        problem.created_by_id = content['created_by_id']

    if 'problem_id' in content:
        problem.problem_id = content['problem_id']

    db.session.add(problem)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "id": problem.id
    })


def problemToDict(problem):
    return {
        'id': problem.id,
        'taken_by_id': problem.taken_by_id,
        'created_by_id': problem.created_by_id,
        'priority': problem.priority,
        'status': problem.status,
        'name': problem.name
    }

# Incidentes

@routes_bp.route('/incident/<id>/comment', methods=['GET'])
def getIncidentComments(incident_id):
    comments = IncidentComment.query.filter_by(incident_id=incident_id)
    return jsonify(list(map(lambda x: x.comment, comments)))

@routes_bp.route('/incident/<id>/comment', methods=['POST'])
def commentIncident(incident_id):
    content = request.json
    if not 'comment' in content:
        return getError('Falta el comentario.')

    comment = IncidentComment(comment=content['comment'], incident_id=incident_id)

    db.session.add(comment)
    db.session.commit()

@routes_bp.route('/incident/<id>/problem', methods=['POST'])
def assignToProblem(incident_id):
    content = request.json
    if not 'problem_id' in content:
        return getError('Falta el comentario.')

    problem = Problem.query.get(content['problem_id'])
    if not problem:
        return getError('Problem_id inválido.')
    incident = Incident.query.get(incident_id)
    incident.status = problem.status
    incident.problem_id = content['problem_id']

    db.session.commit()

@routes_bp.route('/incident', methods=['GET'])
def getIncidents():
    return jsonify(list(map(incidentToDict, Incident.query.all())))

@routes_bp.route('/incident/<id>', methods=['GET'])
def getIncidentById(id):
    return jsonify(incidentToDict(Incident.query.get(id)))

@routes_bp.route('/incident', methods=['POST'])
def postIncident():
    content = request.json
    if not 'name' in content:
        return getError('Faltan atributos obligatorios para un incidente.')

    incident = Incident(name=content['name'], status=Status.CREATED)

    if 'impact' in content:
        incident.impact = content['impact']

    if 'proprity' in content:
        incident.priority = content['priority']

    if 'description' in content:
        incident.description = content['description']

    if 'configuration' in content:
        if not 'configuration_type' in content:
            return getError('Falta el tipo de configuración.')

        if content['configuration_type'] == 'hardware':
            incident.hardware_configuration_id = content['configuration']
        if content['configuration_type'] == 'software':
            incident.software_configuration_id = content['configuration']
        if content['configuration_type'] == 'sla':
            incident.sla_configuration_id = content['configuration']

    if 'created_by_id' in content:
        incident.created_by_id = content['created_by_id']

    if 'taken_by_id' in content:
        incident.taken_by_id = content['taken_by_id']

    if 'problem_id' in content:
        problem = Problem.query.get(content['problem_id'])
        if not problem:
            return getError('Problem_id inválido.')
        incident.status = problem.status
        incident.problem_id = content['problem_id']

    db.session.add(incident)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "id": incident.id
    })


def incidentToDict(incident):
    config_type = None
    config_id = None
    if incident.sla_configuration_id:
        config_id = incident.sla_configuration_id
        config_type = 'sla'

    if incident.software_configuration_id:
        config_id = incident.software_configuration_id
        config_type = 'software'

    if incident.hardware_configuration_id:
        config_id = incident.hardware_configuration_id
        config_type = 'hardware'

    return {
        'id': incident.id,
        'impact': incident.impact,
        'problem_id': incident.problem_id,
        'taken_by_id': incident.taken_by_id,
        'created_by_id': incident.created_by_id,
        'priority': incident.priority,
        'status': incident.status,
        'configuration_id': config_id,
        'configuration_type': config_type,
        'description': incident.description,
        'name': incident.name
    }

def getError(msj):
    return jsonify({
        "status_code": 400,
        "description": msj
    })
