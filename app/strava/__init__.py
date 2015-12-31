from flask import Blueprint
from ..lib.decorators import gen_route_decorator, json_route_decorator

strava = Blueprint('strava', __name__)
route = gen_route_decorator(strava)
as_json = json_route_decorator(strava)

from . import views
