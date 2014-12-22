from . import dates
from flask import request, jsonify
from dateutil.parser import parse
from datetime import timedelta

DATE_FORMAT = "%Y-%m-%d"


@dates.route('/')
def index():
    return "Hello World"


@dates.route('/getdate/<datestring>')
def get_date(datestring):
    parse_dt = parse(datestring)
    delta = request.args.get('delta')
    dt_format = request.args.get('format')
    if format:
        DATE_FORMAT = dt_format

    if delta:
        delta = int(delta)
        new_dt = parse_dt + timedelta(days=delta)
        return new_dt.strftime(DATE_FORMAT)

    return parse_dt.strftime(DATE_FORMAT)
