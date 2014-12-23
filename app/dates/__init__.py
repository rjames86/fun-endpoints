from flask import Blueprint

dates = Blueprint('dates', __name__)

from . import views, errors
