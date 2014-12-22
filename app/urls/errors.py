from flask import jsonify
from . import urls


@urls.app_errorhandler(404)
def page_not_found(e):
    response = jsonify({'error': 'Url not found'})
    response.status_code = 404
    return response

@urls.app_errorhandler(500)
def something_broke(e):
    response = jsonify({'error': 'Shit broke'})
    response.status_code = 500
    return response
