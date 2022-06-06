from flask import Blueprint, request, jsonify

from app.Status import Status
from app.models import Change, Incident, Problem, SoftwareConfiguration, HardwareConfiguration, SLAConfiguration, User, \
    db

# from flask.ext.restplus import Api, Resource, fields
#
# api = Api(app, version='1.0', title='Sample API',
#     description='A sample API',
# )

routes_bp = Blueprint('routes', __name__, )


@routes_bp.route('/', methods=['GET'])
def index():
    return 'Hola'

# Incidentes
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

    if 'problem_id' in content:
        incident.problem_id = content['problem_id']

    db.session.add(incident)
    db.session.commit()
    return jsonify({
        "status_code": 201,
        "codigo": incident.id
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
