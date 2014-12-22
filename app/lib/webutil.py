from utils import configure_log, make_error
from flask import request
from functools import update_wrapper


import logging

all_tokens = {
    'ryan': 'zyxwvut'
}

def add_context(f):
    def log():
        logger = configure_log(logging.INFO, 'fun-endpoints', __name__)
        logger.info(dict(
            path=request.path,
            endpoint=request.endpoint,
            args=dict(request.args)
            )
        )

    def inner(*args, **kw):
        log()
        return f(*args, **kw)
    return inner


def gen_route_decorator(mod):
    class route(object):
        def __init__(self, path):
            self.path = path

        def __call__(self, f):
            # Flask has a lookup table with function name, so we need to pass it through
            f_with_context_and_json = add_context(f)
            f_with_context_and_json.__name__ = f.__name__
            return mod.route(self.path, methods=['POST', 'GET'])(f_with_context_and_json)
    return route


def require_token(restrict=None):
    if restrict and not isinstance(restrict, list):
        restrict = [restrict]

    def outer(f):
        def inner(*args, **kw):
            token = request.args.get('token')
            if not token:
                return make_error(403, "Acess forbidden")
            if restrict and not any(all_tokens.get(user)== token for user in restrict):
                return make_error(403, "Acess forbidden")
            if not any(all_tokens[user] for user in all_tokens):
                return make_error(403, "Acess forbidden")
            return f(*args, **kw)
        return update_wrapper(inner, f)
    return outer
