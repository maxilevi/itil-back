from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

#class Incidente(db.Model):
    #codigo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #nombre = db.Column(db.String, nullable=False)
