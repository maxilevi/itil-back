from flask import Blueprint, request, jsonify
from flask_sqlalchemy import inspect
from app.Status import Status
from app.models import Change, Incident, Problem, ConfigurationData, Configuration, IncidentConfiguration, ProblemComment, IncidentComment, KnownErrors, db, ChangeComment

routes_bp = Blueprint('routes', __name__, )


@routes_bp.route('/', methods=['GET'])
def index():
    return 'Hola'


########################## Configuration #########################

def create_config_data(id, version, content):
    config_data = ConfigurationData(config_id=id, version_number=version)
    for key, value in content.items():
        setattr(config_data, key, value)
    return config_data, None, None

@routes_bp.route('/config', methods=['POST'])
def postConfig():
    content = request.json
    if not 'config_type' in content:
        return None, 'Falta el tipo de configuracion', 400

    if not 'name' in content:
        return None, 'Falta el nombre de configuracion', 400
    config = Configuration()
    config.current_version = 1

    db.session.add(config)
    db.session.flush()
    db.session.refresh(config)

    config_data, error, errno = create_config_data(config.id, 1, content)
    if not config_data:
        return error, errno

    db.session.add(config_data)
    db.session.commit()
    return jsonify({
        "id": config.id
    }), 201


@routes_bp.route('/config/<id>', methods=['POST'])
def updateConfigValues(id):
    content = request.json
    config = Configuration.query.get(id)
    if not config:
        return 'No existe esa config', 404

    if not "user_id" in content:
        return 'Falta el user_id', 400

    db.session.add(config)
    db.session.flush()
    db.session.refresh(config)

    prev_versions = ConfigurationData.query.filter_by(config_id=id)
    config_data, error, errno = create_config_data(config.id, max(map(lambda x: x.version_number, prev_versions)) + 1, content)

    if not config_data:
        return error, errno

    config.current_version = config_data.version_number
    createChangeFromConfig(config, content['user_id'], config_data)
    db.session.add(config_data)
    db.session.commit()
    return jsonify({
        "id": config.id
    }), 201

def createChangeFromConfig(config, user_id, config_data):
    content = {
        "name": "Cambio de versión de la configuración: " + config_data.name,
        "description": "Se debe ejecutar el cambio de versión a la NRO: " + str(config.current_version),
        "priority": "Media",
        "created_by_id": user_id,
        "status": Status.CREATED
    }
    return createChange(content)

@routes_bp.route('/config/<id>', methods=['PATCH'])
def updateConfigAttributes(id):
    content = request.json
    config = Configuration.query.get(id)
    if not config:
        return 'No existe esa config', 404

    if not 'current_version' in content:
        return 'No current version specified', 500

    config.current_version = content["current_version"]
    db.session.commit()
    return jsonify({
        "id": config.id
    }), 201

@routes_bp.route('/config/<id>', methods=['DELETE'])
def deleteConfig(id):
    config = Configuration.query.get(id)
    prev_versions = ConfigurationData.query.filter_by(config_id=id)
    for v in prev_versions:
        db.session.delete(v)

    db.session.delete(config)
    db.session.commit()
    return jsonify({
    }), 200


@routes_bp.route('/config/<id>', methods=['GET'])
def getConfig(id):
    config = Configuration.query.get(id)
    if not config:
        return 'No existe esa config', 404

    return jsonify(getConfigDict(config)), 201

@routes_bp.route('/config', methods=['GET'])
def getAllConfigs():
    return jsonify(list(map(getConfigDict, Configuration.query.all())))

def getConfigDict(config):
    return {
        "config": {
                **configToDict(config.id),
                **({'current_version': config.current_version})
            }
        }

def getConfigDictFromIncident(config_id):
    config = Configuration.query.get(config_id)
    return {
            **configToDict(config_id),
            **({'current_version': config.current_version})
           }

########################## Known Errors ##########################

@routes_bp.route('/knownError/<id>/solve', methods=['POST'])
def solveKnownError(id):
    content = request.json
    if not 'solution' in content:
        return getError("Falta la solución"), 400
    knownError = KnownErrors.query.get(id)
    if knownError == None:
        return getError("No existe ese error"), 400
    knownError.solution = content['solution']
    db.session.commit()

    return "", 200

@routes_bp.route('/knownError', methods=['GET'])
def getKnownErrors():
    return jsonify(list(map(knownErrorToDict, KnownErrors.query.all())))

@routes_bp.route('/knownError/<id>', methods=['GET'])
def getKnownErrorsById(id):
    knownError = KnownErrors.query.get(id)
    if knownError == None:
        return getError("No existe ese error"), 400
    return jsonify(knownErrorToDict(knownError))

@routes_bp.route('/knownError', methods=['POST'])
def postKnownErrors():
    content = request.json

    if not 'name' in content or not 'description' in content:
        return getError("Falta el nombre o la descripción del error"), 400

    knownError = KnownErrors(name=content['name'], description=content['description'])

    if 'solution' in content:
        knownError.solution = content['solution']

    db.session.add(knownError)
    db.session.commit()
    return jsonify({
        "id": knownError.id
    }), 201

@routes_bp.route('/knownError/<id>', methods=['DELETE'])
def deleteKnownError(id):
    knownError = KnownErrors.query.get(id)
    if knownError == None:
        return getError("No existe ese error"), 400
    db.session.delete(knownError)
    db.session.commit()
    return id, 200

def knownErrorToDict(knownError):
    return {
        'id': knownError.id,
        'description' : knownError.description,
        'name': knownError.name,
        'solution': knownError.solution,
        'created_on': knownError.created_on
    }

########################## Changes ###############################

@routes_bp.route('/change/<id>', methods=['DELETE'])
def deleteChange(id):
    change = Change.query.get(id)
    if change == None:
        return getError("No existe ese cambio"), 400
    db.session.delete(change)
    db.session.commit()
    return id, 200

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
    if not 'name' in content:
        return getError('Faltan atributos obligatorios para un cambio.'), 400

    change = createChange(content)

    return jsonify({
        "id": change.id
    }), 201

def createChange(content):
    change = Change(name=content['name'], status=Status.CREATED)

    if 'description' in content:
        change.description = content['description']

    if 'priority' in content:
        change.priority = content['priority']

    if 'created_by_id' in content:
        change.created_by_id = content['created_by_id']

    if 'taken_by_id' in content:
        change.taken_by_id = content['taken_by_id']

    if 'problem_id' in content:
        change.problem_id = content['problem_id']

    if 'incident_id' in content:
        change.incident_id = content['incident_id']

    if 'impact' in content:
        change.impact = content['impact']

    db.session.add(change)
    db.session.commit()
    return change

@routes_bp.route('/change/<id>/comment', methods=['GET'])
def getChangeComments(id):
    comments = ChangeComment.query.filter_by(change_id=id)
    return jsonify(list(map(lambda x: object_as_dict(x), comments)))

@routes_bp.route('/change/<id>/comment', methods=['POST'])
def commentChange(id):
    content = request.json
    if not 'comment' in content or not 'user_id' in content:
        return getError('Falta el comentario o usuario.'), 400

    comment = ChangeComment(comment=content['comment'], change_id=id, user_id=content['user_id'])

    db.session.add(comment)
    db.session.commit()
    return "", 200

@routes_bp.route('/change/<id>/take', methods=['POST'])
def takeChange(id):
    content = request.json
    if not 'taken_by_id' in content:
        return getError('Falta el ID del usuario.'), 400
    change = Change.query.get(id)
    change.taken_by_id = content['taken_by_id']
    change.status = Status.TAKEN
    db.session.commit()
    return "", 200

@routes_bp.route('/change/<id>/solve', methods=['POST'])
def solveChange(id):
    change = Change.query.get(id)
    change.status = Status.SOLVED
    db.session.commit()
    return "", 200

def changeToDict(change):
    incident = Incident.query.get(change.incident_id)
    return {
        'id': change.id,
        'description' : change.description,
        'created_by_id': change.created_by_id,
        'taken_by_id' : change.taken_by_id,
        'priority': change.priority,
        'name': change.name,
        'problem_id' : change.problem_id,
        'status': change.status,
        'created_on': change.created_on,
        'impact': change.impact,
        'incident': incidentToDict(incident) if incident else None
    }


########################## Problems ##########################

@routes_bp.route('/problem/<id>', methods=['DELETE'])
def deleteProblem(id):
    problem = Problem.query.get(id)
    if problem == None:
        return getError("No existe ese problema"), 400
    db.session.delete(problem)
    db.session.commit()
    return id, 200

@routes_bp.route('/problem/<id>/comment', methods=['GET'])
def getProblemComments(id):
    comments = ProblemComment.query.filter_by(problem_id=id)
    return jsonify(list(map(lambda x: object_as_dict(x), comments)))

@routes_bp.route('/problem/<id>/comment', methods=['POST'])
def commentProblem(id):
    content = request.json
    if not 'comment' in content or not 'user_id' in content:
        return getError('Falta el comentario o usuario.'), 400

    comment = ProblemComment(comment=content['comment'], problem_id=id, user_id=content['user_id'])

    db.session.add(comment)
    db.session.commit()
    return "", 200

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
def takeProblem(id):
    content = request.json
    if not 'taken_by_id' in content:
        return getError('Falta el ID del usuario.'), 400

    incidents = Incident.query.filter_by(problem_id=id)
    for incident in incidents:
        incident.status = Status.TAKEN

    problem = Problem.query.get(id)
    problem.taken_by_id = content['taken_by_id']
    problem.status = Status.TAKEN
    db.session.commit()
    return "", 200

@routes_bp.route('/problem/<id>/solve', methods=['POST'])
def solveProblem(id):
    problem = Problem.query.get(id)
    problem.status = Status.SOLVED

    incidents = Incident.query.filter_by(problem_id=id)
    for incident in incidents:
        incident.status = Status.SOLVED

    db.session.commit()
    return "", 200

@routes_bp.route('/problem', methods=['POST'])
def postProblem():
    content = request.json
    if not 'name' in content:
        return getError('Faltan atributos obligatorios para un problema.'), 400

    problem = Problem(name=content['name'], status=Status.CREATED)

    if 'priority' in content:
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
        'name': problem.name,
        'created_on': problem.created_on
    }


########################## Incidentes ##########################

@routes_bp.route('/incident/<id>', methods=['DELETE'])
def deleteIncident(id):
    incident = Incident.query.get(id)
    if incident == None:
        return getError("No existe ese incidente"), 400
    db.session.delete(incident)
    db.session.commit()
    return id, 200

@routes_bp.route('/incident/<id>/take', methods=['POST'])
def takeIncident(id):
    content = request.json
    if not 'taken_by_id' in content:
        return getError('Falta el ID del usuario.'), 400
    incident = Incident.query.get(id)
    incident.taken_by_id = content['taken_by_id']
    incident.status = Status.TAKEN
    db.session.commit()
    return "", 200

@routes_bp.route('/incident/<id>/solve', methods=['POST'])
def solveIncident(id):
    incident = Incident.query.get(id)
    incident.status = Status.SOLVED
    db.session.commit()
    return "", 200

@routes_bp.route('/incident/<id>/comment', methods=['GET'])
def getIncidentComments(id):
    comments = IncidentComment.query.filter_by(incident_id=id)
    return jsonify(list(map(lambda x: object_as_dict(x), comments)))

@routes_bp.route('/incident/<id>/comment', methods=['POST'])
def commentIncident(id):
    content = request.json
    if not 'comment' in content or not 'user_id' in content:
        return getError('Falta el comentario o usuario.'), 400

    comment = IncidentComment(comment=content['comment'], incident_id=id, user_id=content['user_id'])

    db.session.add(comment)
    db.session.commit()
    return "", 200

@routes_bp.route('/incident/<id>/problem', methods=['POST'])
def assignToProblem(id):
    content = request.json
    if not 'problem_id' in content:
        return getError('Falta el comentario.'), 400

    problem = Problem.query.get(content['problem_id'])
    if not problem:
        return getError('Problem_id inválido.'), 400
    incident = Incident.query.get(id)
    incident.status = problem.status
    incident.problem_id = content['problem_id']

    db.session.commit()
    return "", 200

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

    if 'priority' in content:
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
            incident_configuration = IncidentConfiguration(incident_id=incident.id, configuration_id=id)
            db.session.add(incident_configuration)

    db.session.commit()
    return jsonify({
        "id": incident.id
    }), 201

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

def configToDict(config_id):
    versions = ConfigurationData.query.filter_by(config_id=config_id)
    print(versions)
    return {
        'id': config_id,
        'versions': sorted(list(map(object_as_dict, versions)), key=lambda x: x['version_number'])
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
        'configurations': list(map(getConfigDictFromIncident, map(lambda x: x.configuration_id, IncidentConfiguration.query.filter_by(incident_id=incident.id)))),
        'description': incident.description,
        'name': incident.name,
        'created_on': incident.created_on
    }

def getError(msj):
    return jsonify({
        "error": msj
    })
