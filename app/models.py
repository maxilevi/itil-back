from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class ConfigurationData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_id = db.Column(db.Integer, db.ForeignKey("configuration.id"))
    version_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    config_type = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=True)
    version = db.Column(db.String, nullable=True)
    provider = db.Column(db.String, nullable=True)
    licences = db.Column(db.String, nullable=True)
    acceptance_date = db.Column(db.Date, nullable=True)
    service = db.Column(db.String, nullable=True)
    service_manager = db.Column(db.String, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    crucial = db.Column(db.Boolean, nullable=True)
    location = db.Column(db.String, nullable=True)
    price = db.Column(db.Integer, nullable=True)
    installation_date = db.Column(db.Date, nullable=True)
    capacity = db.Column(db.Integer, nullable=True)
    serial_number = db.Column(db.String, nullable=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

class Configuration(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    current_version = db.Column(db.Integer, nullable=False)

class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    priority = db.Column(db.String)
    status = db.Column(db.String)
    created_by_id = db.Column(db.String)
    taken_by_id = db.Column(db.String)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    problem_id = db.Column(db.Integer, db.ForeignKey("problem.id"))
    name = db.Column(db.String, nullable=False)
    priority = db.Column(db.String)
    created_by_id = db.Column(db.String)
    taken_by_id = db.Column(db.String)
    description = db.Column(db.String)
    impact = db.Column(db.String)
    status = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

class IncidentConfiguration(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incident.id"))
    configuration_id = db.Column(db.Integer, db.ForeignKey("configuration.id"), nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

class Change(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    priority = db.Column(db.String)
    created_by_id = db.Column(db.String)
    problem_id = db.Column(db.Integer, db.ForeignKey("problem.id"))
    incident_id = db.Column(db.Integer, db.ForeignKey("incident.id"))
    status = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

class ChangeComment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String)
    comment = db.Column(db.String)
    change_id = db.Column(db.Integer, db.ForeignKey("change.id"))
    created_on = db.Column(db.DateTime, server_default=db.func.now())

class ProblemComment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.String)
    user_id = db.Column(db.String)
    problem_id = db.Column(db.Integer, db.ForeignKey("problem.id"))
    created_on = db.Column(db.DateTime, server_default=db.func.now())

class IncidentComment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.String)
    user_id = db.Column(db.String)
    incident_id = db.Column(db.Integer, db.ForeignKey("incident.id"))
    created_on = db.Column(db.DateTime, server_default=db.func.now())

class KnownErrors(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    solution = db.Column(db.String)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
