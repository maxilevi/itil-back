from flask import Blueprint, request, jsonify

from app.Status import Status
from app.models import Change, Incident, Problem, IncidentConfiguration, ProblemComment, IncidentComment, db

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
    change = Change.query.get(id)
    if change == None:
        return getError("No existe ese cambio"), 400
    return jsonify(changeToDict(change))

@routes_bp.route('/change', methods=['POST'])
def postChange():
    content = request.json
    if not 'name' in content or 'problem_id' not in content:
        return getError('Faltan atributos obligatorios para un cambio.'), 400

    change = Change(name=content['name'], status=Status.CREATED, problem_id=content['problem_id'])

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
        "id": change.id
    }), 201

def changeToDict(change):
    return {
        'id': change.id,
        'description' : change.description,
        'created_by_id': change.created_by_id,
        'priority': change.priority,
        'name': change.name,
        'problem_id' : change.problem_id,
        'status': change.status,
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
        return getError('Falta el comentario.'), 400

    comment = ProblemComment(comment=content['comment'], problem_id=problem_id)

    db.session.add(comment)
    db.session.commit()

@routes_bp.route('/problem', methods=['GET'])
def getProblems():
    return jsonify(list(map(problemToDict, Problem.query.all())))

@routes_bp.route('/problem/<id>', methods=['GET'])
def getProblemById(id):
    problem = Problem.query.get(id)
    if problem is None:
        return getError("No existe ese problema."), 400
    return jsonify(problemToDict(problem))

@routes_bp.route('/problem/<id>/take', methods=['POST'])
def takeProblem(problem_id):
    content = request.json
    if not 'taken_by_id' in content:
        return getError('Falta el ID del usuario.'), 400

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
        return getError('Faltan atributos obligatorios para un problema.'), 400

    problem = Problem(name=content['name'], status=Status.CREATED)

    if 'proprity' in content:
        problem.priority = content['priority']

    if 'created_by_id' in content:
        problem.created_by_id = content['created_by_id']

    if 'problem_id' in content:
        problem.problem_id = content['problem_id']

    db.session.add(problem)
    db.session.flush()
    db.session.refresh(problem)

    if 'incident_ids' in content:
        for id in content['incident_ids']:
            incident = Incident.query.get(id)
            incident.problem_id = problem.id

    db.session.commit()
    return jsonify({
        "id": problem.id
    }), 201


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
        return getError('Falta el comentario.'), 400

    comment = IncidentComment(comment=content['comment'], incident_id=incident_id)

    db.session.add(comment)
    db.session.commit()

@routes_bp.route('/incident/<id>/problem', methods=['POST'])
def assignToProblem(incident_id):
    content = request.json
    if not 'problem_id' in content:
        return getError('Falta el comentario.'), 400

    problem = Problem.query.get(content['problem_id'])
    if not problem:
        return getError('Problem_id inválido.'), 400
    incident = Incident.query.get(incident_id)
    incident.status = problem.status
    incident.problem_id = content['problem_id']

    db.session.commit()

@routes_bp.route('/incident', methods=['GET'])
def getIncidents():
    return jsonify(list(map(incidentToDict, Incident.query.all())))

@routes_bp.route('/incident/<id>', methods=['GET'])
def getIncidentById(id):
    incident = Incident.query.get(id)
    if incident == None:
        return getError("No existe ese incidente."), 400
    return jsonify(incidentToDict(incident))

@routes_bp.route('/incident', methods=['POST'])
def postIncident():
    content = request.json
    if not 'name' in content:
        return getError('Faltan atributos obligatorios para un incidente.'), 400

    incident = Incident(name=content['name'], status=Status.CREATED)

    if 'impact' in content:
        incident.impact = content['impact']

    if 'proprity' in content:
        incident.priority = content['priority']

    if 'description' in content:
        incident.description = content['description']

    if 'created_by_id' in content:
        incident.created_by_id = content['created_by_id']

    if 'taken_by_id' in content:
        incident.taken_by_id = content['taken_by_id']

    if 'problem_id' in content:
        problem = Problem.query.get(content['problem_id'])
        if not problem:
            return getError('Problem_id inválido.'), 404
        incident.status = problem.status
        incident.problem_id = content['problem_id']

    db.session.add(incident)
    db.session.flush()
    db.session.refresh(incident)

    if 'configuration_ids' in content:
        for id in content['configuration_ids']:
            incident_configuration = IncidentConfiguration(indicent_id=incident.id, configuration_id=id)
            db.session.add(incident_configuration)

    db.session.commit()
    return jsonify({
        "id": incident.id
    }), 201

# TODO: esto se tiene que adaptar al nuevo modelo de configuraciones, ahora devuelve una poronga
def configToDict(incident_config):
    # config_type = None
    # config_id = None
    # if incident_config.sla_configuration_id:
    #     config_id = incident_config.sla_configuration_id
    #     config_type = 'sla'
    #
    # if incident_config.software_configuration_id:
    #     config_id = incident_config.software_configuration_id
    #     config_type = 'software'
    #
    # if incident_config.hardware_configuration_id:
    #     config_id = incident_config.hardware_configuration_id
    #     config_type = 'hardware'

    return {
        'id': incident_config.id
    }

def incidentToDict(incident):

    return {
        'id': incident.id,
        'impact': incident.impact,
        'problem_id': incident.problem_id,
        'taken_by_id': incident.taken_by_id,
        'created_by_id': incident.created_by_id,
        'priority': incident.priority,
        'status': incident.status,
        'configurations': map(configToDict, IncidentConfiguration.query.filter_by(incident_id=incident.id)),
        'description': incident.description,
        'name': incident.name
    }

def getError(msj):
    return jsonify({
        "error": msj
    })
