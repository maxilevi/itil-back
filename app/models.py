from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# class HardwareConfiguration(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String, nullable=False)

# class SLAConfiguration(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String, nullable=False)
#
# class SoftwareConfiguration(db.Model):
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String, nullable=False)

class Configuration(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    configuration_type = db.Column(db.String)
    name = db.Column(db.String, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    mail = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    priority = db.Column(db.String)
    status = db.Column(db.String)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    configuration_id = db.Column(db.Integer, db.ForeignKey("configuration.id"))
    problem_id = db.Column(db.Integer, db.ForeignKey("problem.id"))
    name = db.Column(db.String, nullable=False)
    priority = db.Column(db.String)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    description = db.Column(db.String)
    impact = db.Column(db.String)
    status = db.Column(db.String, nullable=False)

class Change(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String)
    priority = db.Column(db.String)
    status = db.Column(db.String)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))

