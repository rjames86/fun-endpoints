from flask import Flask
from flask.ext.bootstrap import Bootstrap
from config import config
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from lib.webutils import ProxiedRequest

bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
db = SQLAlchemy()
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
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    from .urls import urls as url_blueprint
    from .admin import admin as admin_blueprint
    from .auth import auth as auth_blueprint
    from .apartment import apartment as apartment_blueprint
    from .strava import strava as strava_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(url_blueprint, url_prefix='/urls')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(apartment_blueprint, url_prefix='/apartment')
    app.register_blueprint(strava_blueprint, url_prefix='/strava')

    if not app.config['SSL_DISABLE']:
        from flask.ext.sslify import SSLify
        sslify = SSLify(app)

    return app
