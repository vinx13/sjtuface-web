from flask import Blueprint
from flask_restful import Api

#_api = Blueprint('api', __name__)
api = Api(prefix="/api")

from . import views