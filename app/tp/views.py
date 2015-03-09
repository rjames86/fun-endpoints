from . import dates
from ..lib.decorators import require_token
from ..lib.utils import make_error
from flask import request, jsonify, abort


@tp.route('/')
def index():
    return "Hello World"


@tp.route('/test/<thing>')
def thing(thing):
    return thing