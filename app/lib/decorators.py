from utils import configure_log, make_error
from flask import request, jsonify
from functools import update_wrapper
from werkzeug.contrib.cache import SimpleCache
from ..models import User

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


def as_json_context(f):
    def format_output(ret):
        data = []
        if not isinstance(ret, list):
            ret = [ret]
        for item in ret:
            try:
                data.append(item._asdict())
            except AttributeError:
                data.append(item)
        return jsonify(data=data)

    def inner(*args, **kwargs):
        return format_output(f(*args, **kwargs))
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

def json_route_decorator(mod):
    class route(object):
        def __init__(self, path):
            self.path = path

        def __call__(self, f):
            # Flask has a lookup table with function name, so we need to pass it through
            f_with_context_and_json = as_json_context(f)
            f_with_context_and_json.__name__ = f.__name__
            return mod.route(self.path, methods=['POST', 'GET'])(f_with_context_and_json)
    return route


def require_token(restrict=None):
    if restrict and not isinstance(restrict, list):
        restrict = [restrict]

    def outer(f):
        def inner(*args, **kw):
            all_tokens = User.token_dict()
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

CACHE_TIMEOUT = 300
cache = SimpleCache()

class cached(object):

    def __init__(self, timeout=None):
        self.timeout = timeout or CACHE_TIMEOUT

    def __call__(self, f):
        def decorator(*args, **kwargs):
            response = cache.get(request.path)
            if response is None:
                response = f(*args, **kwargs)
                cache.set(request.path, response, self.timeout)
            return response
        return decorator
