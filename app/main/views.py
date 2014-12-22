from . import route


@route('/')
def index():
    return "Hello World."
