from utils import configure_log
from flask import request

import logging

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
