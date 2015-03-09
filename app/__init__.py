from flask import Flask
from flask.ext.bootstrap import Bootstrap
from config import config
from flask.ext.login import LoginManager
from lib.webutils import ProxiedRequest

bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.request_class = ProxiedRequest

    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    from .urls import urls as url_blueprint
    from .dates import dates as dates_blueprint
    from .admin import admin as admin_blueprint
    from .auth import auth as auth_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(url_blueprint, url_prefix='/urls')
    app.register_blueprint(dates_blueprint, url_prefix='/dates')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask.ext.sslify import SSLify
        sslify = SSLify(app)

    return app
