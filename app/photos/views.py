from flask import (
    request,
    render_template,
    session,
    url_for,
    redirect,
    jsonify
)
import dropbox
from flask import Response
from . import photos
from ..lib.fakelist import fakelist
from ..lib.utils import get_thumbnail

ACCESS_TOKEN = 't5NGncEdlEYAAAAAAAKKLr-Xw4V1AtF_Dy5XwfGwJudP93VDrM3jfiHharh3rXq1'

@photos.route('/')
def index():
    return render_template('photos/index.html')

@photos.route('/get_photos', methods=['GET'])
def get_photos():
    start = request.args.get('start')
    limit = request.args.get('limit')
    client = dropbox.client.DropboxClient(access_token)
    filelist = sorted(
        client.metadata(
            '/Pictures/Picture a day',
            list=True
        ).get('contents', []),
        key=_filelist_sorter
    )
    # filelist = sorted(
    #     fakelist,
    #     key=_filelist_sorter
    # )

    if start:
        filelist = filelist[_get_file_index(start, filelist):]
    if limit:
        filelist = filelist[:int(limit)]

    return jsonify(
        dict(
            data=filelist
        )
    )


@photos.route('/thumbnail', methods=['GET'])
def thumbnail():
    path = request.args.get('path')
    get_thumb = get_thumbnail(path)
    return url_for('static', filename='images/photos/%s' % get_thumb)

def _filelist_sorter(f):
    return f['path']

def _get_file_index(filepath, filelist):
    for index, item in enumerate(filelist):
        if item['path'] == filepath:
            return index


@photos.route('/testing')
def testing():
    import os
    print "MYPATH", os.getcwd()
    f = open('app/photos/img.jpg', 'rb')
    return Response(f.read(), mime_type='image/jpeg')
