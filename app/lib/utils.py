import logging
import os
from flask import jsonify

APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_STATIC = os.path.join(APP_ROOT, 'static')


def configure_log(level=None, name=None, verbose=False):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    return logger


def get_var(var):
    return os.environ.get(var)


def make_error(status_code, message):
    response = jsonify({
        'status': status_code,
        'message': message,
    })
    response.status_code = status_code
    return response
