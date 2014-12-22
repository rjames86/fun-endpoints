from flask import Blueprint

urls = Blueprint('urls', __name__)

from . import views
