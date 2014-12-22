from . import dates, errors
from flask import request, jsonify, abort
from dateutil.parser import parse
from datetime import timedelta


@dates.route('/')
def index():
    return "Hello World"


@dates.route('/getdate/<datestring>')
def get_date(datestring):
    DATE_FORMAT = "%Y-%m-%d"

    parse_dt = parse(datestring)
    delta = request.args.get('delta')
    dt_format = request.args.get('format')
    if dt_format:
        DATE_FORMAT = dt_format

    if delta:
        try:
            delta = int(delta)
        except ValueError:
            return errors.make_error(
                500,
                "This doesn't look like an int. Try again..."
            )
        new_dt = parse_dt + timedelta(days=delta)
        return new_dt.strftime(DATE_FORMAT)

    return parse_dt.strftime(DATE_FORMAT)
