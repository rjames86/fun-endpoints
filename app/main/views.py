from flask import (
    jsonify,
    request
)
from . import main


@main.route('/')
def index():
    return "Hello World."


@main.route("/ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200
