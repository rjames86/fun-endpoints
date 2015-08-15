from flask import Blueprint
from ..lib.decorators import gen_route_decorator, json_route_decorator

main = Blueprint('main', __name__)
route = gen_route_decorator(main)
as_json = json_route_decorator(main)

from . import views
