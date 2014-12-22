from flask import Flask
from flask.ext.bootstrap import Bootstrap
from config import config

bootstrap = Bootstrap()

def create_app(config_name):
      app = Flask(__name__)
      app.config.from_object(config[config_name])
      config[config_name].init_app(app)

      bootstrap.init_app(app)

      from .main import main as main_blueprint
      from .urls import urls as url_blueprint
      app.register_blueprint(main_blueprint, url_prefix='/')
      app.register_blueprint(url_blueprint, url_prefix='/urls')

      return app
