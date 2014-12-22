import logging


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
