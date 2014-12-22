from . import main
from flask import request


@main.route('/')
def index():
    return "Hello World."

@main.route('/today')
def get_date():
    import datetime
    return  datetime.datetime.today().strftime("%Y-%m-%d")

@main.route('/tomorrow')
def get_tomorrow():
    import datetime
    date = request.args.get('date')
    parse_dt = datetime.datetime.strptime(x, "%Y-%m-%d")
    return parse_dt + datetime.datetime.timedelta(days=1)
