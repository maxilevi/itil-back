from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class HardwareConfiguration(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    provider = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    installation_date = db.Column(db.Date, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    serial_number = db.Column(db.String, nullable=False)

class SLAConfiguration(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    version = db.Column(db.String, nullable=False)
    provider = db.Column(db.String, nullable=False)
    licences = db.Column(db.String, nullable=False)
    acceptance_date = db.Column(db.Date, nullable=False)

class SoftwareConfiguration(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    service = db.Column(db.String, nullable=False)
    service_manager = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    crucial = db.Column(db.Boolean, nullable=False)

class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    priority = db.Column(db.String)
    status = db.Column(db.String)
    created_by_id = db.Column(db.String)
    taken_by_id = db.Column(db.String)

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

class IncidentConfiguration(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incident.id"))
    software_configuration_id = db.Column(db.Integer, db.ForeignKey("software_configuration.id"), nullable=True)
    hardware_configuration_id = db.Column(db.Integer, db.ForeignKey("hardware_configuration.id"), nullable=True)
    sla_configuration_id = db.Column(db.Integer, db.ForeignKey("sla_configuration.id"), nullable=True)

class Change(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String)
    priority = db.Column(db.String)
    created_by_id = db.Column(db.String)
    problem_id = db.Column(db.Integer, db.ForeignKey("problem.id"))
    status = db.Column(db.String, nullable=False)

class ProblemComment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.String)
    problem_id = db.Column(db.Integer, db.ForeignKey("problem.id"))

class IncidentComment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.String)
    incident_id = db.Column(db.Integer, db.ForeignKey("incident.id"))