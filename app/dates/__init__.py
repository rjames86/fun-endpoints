from flask import Blueprint
from ..lib.webutil import gen_route_decorator

dates = Blueprint('dates', __name__)

from . import views, errors
