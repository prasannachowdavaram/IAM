from flask import Flask
from .config import config
import os

STATIC_PATH = os.path.abspath('static/angular/dist')

def create_app(config_name):
    app = Flask(__name__, static_folder=STATIC_PATH)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    from .views import api
    app.register_blueprint(api.mod)    
    
    return app