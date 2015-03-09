from flask import Blueprint

tp = Blueprint('tp', __name__)

from . import views
