from flask import Blueprint, request, jsonify
from app.models import db

routes_bp = Blueprint('routes', __name__,)

@routes_bp.route('/', methods=['GET'])
def index():
    return 'Hola'
