from flask import Blueprint
from ..lib.decorators import gen_route_decorator

urls = Blueprint('urls', __name__)
route = gen_route_decorator(urls)

from . import views, errors
