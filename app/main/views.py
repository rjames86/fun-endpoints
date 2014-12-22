from flask import render_template, session, url_for, jsonify, request, abort
import os
from . import main


@main.route('/long_url', methods=['GET'])
def long_url():
    import urllib
    token = request.args.get('token', False)
    if not bool(token and token != os.environ.get('REQUEST_TOKEN')):
        abort(403)
    url = request.args.get('url', None)
    if not url:
        abort(400, {'message': 'missing parameter: url'})
    resp = urllib.urlopen(url)
    if not resp.getcode() == 200:
        abort(500)
    return jsonify(
        short_url=url,
        long_url=resp.url
    )

@main.errorhandler(400)
def custom400(error):
    return jsonify({'message': error.description['message']})
