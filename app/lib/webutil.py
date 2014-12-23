from utils import configure_log, make_error
from flask import request
from functools import update_wrapper
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


from flask import Request

class ProxiedRequest(Request):
    """
    https://gist.github.com/elidickinson/4166628
    `Request` subclass that overrides `remote_addr` with Frontend Server's
    HTTP_X_FORWARDED_FOR when available.

    from real_ip_address import ProxiedRequest
    app = [...]
    app.request_class = ProxiedRequest

    """

    @property
    def remote_addr(self):
        """The remote address of the client."""
        # Get a parsed version of X-Forwarded-For header (contains
        #    REMOTE_ADDR if no forwarded-for header). See
        #    http://en.wikipedia.org/wiki/X-Forwarded-For
        fwd = self.access_route
        remote = self.environ.get('REMOTE_ADDR', None)
        if fwd and self._is_private_ip(remote):
            # access route is a list where the client is first
            # followed by any intermediary proxies. However, we
            # can only trust the last entry as valid -- it's from
            # the server one hop behind the one connecting.
            return fwd[-1]
        else:
            return remote

    def _is_private_ip(self,ip):
        blank_ip = (ip is None or ip == '')
        private_ip = (ip.startswith('10.') or ip.startswith('172.16.') or ip.startswith('192.168.'))
        local_ip = (ip == '127.0.0.1' or ip == '0.0.0.0')
        return blank_ip or private_ip or local_ip
