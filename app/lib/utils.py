import logging
import os
from flask import (
    jsonify,
    current_app
)
import dropbox
from werkzeug import secure_filename

ACCESS_TOKEN = 't5NGncEdlEYAAAAAAAKKLr-Xw4V1AtF_Dy5XwfGwJudP93VDrM3jfiHharh3rXq1'

def configure_log(level=None, name=None, verbose=False):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # file_handler = logging.FileHandler('%s.log' % name, 'a+', 'utf-8')
    # file_handler.setLevel(logging.DEBUG)
    # file_format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d in %(funcName)s]')
    # file_handler.setFormatter(file_format)
    # logger.addHandler(file_handler)

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

def get_thumbnail(path):
    import cStringIO
    from PIL import Image
    import os

    app = current_app._get_current_object()

    formats = {
        'image/jpeg': 'JPEG',
        'image/png': 'PNG',
        'image/gif': 'GIF'
    }

    client = dropbox.client.DropboxClient(ACCESS_TOKEN)
    response = client.thumbnail(path)
    image_type = response.getheader('content-type')
    print image_type
    try:
        format = formats[image_type]
    except KeyError:
        raise ValueError('Not a supported image format')

    file = cStringIO.StringIO(response.read())
    img = Image.open(file)

    print "CURPATH", os.getcwd()
    filename = secure_filename(path.rpartition('/')[-1])
    img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename), format=format)
    return filename
