from flask import Blueprint, jsonify
from flask_cors import cross_origin

api = Blueprint('api', __name__)


from . import views, errors
