from flask import (
    jsonify,
    request,
    abort
)
from . import urls, errors
from ..lib import utils
from ..lib.decorators import require_token
from ..lib.yourls import client as yourls_client
from BeautifulSoup import BeautifulSoup as Soup
import urllib


@urls.route('/')
def index():
    return "Hello Urls."


@urls.route('/long_url')
def long_url():
    token = request.args.get('token', False)
    if token != utils.get_var('REQUEST_TOKEN'):
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


@urls.route('/shorten')
@require_token(restrict='rjames')
def yourls():
    username = utils.get_var('yourls_user')
    password = utils.get_var('yourls_pw')
    api_url = utils.get_var('yourls_url')
    to_shorten = request.args.get('url')
    if not to_shorten:
        return utils.make_error(400, "Missing url param")
    c = yourls_client.YourlsClient(
        api_url, username=username,
        password=password
    )
    short_url = c.shorten(to_shorten)

    open_site = urllib.urlopen(to_shorten)
    soup = Soup(open_site)
    title_search = soup.find('title')
    title = title_search.text.strip() if title_search else ''

    return jsonify(
        url=short_url,
        title=title
    )
