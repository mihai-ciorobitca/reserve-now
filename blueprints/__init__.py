from flask import Flask
from .admin import admin_blueprint
from .auth import auth_blueprint
from .errors import errors_blueprint
from .home import home_blueprint
from .main import main_blueprint
from os import getenv

from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="../views")
    
    app.secret_key = getenv("SECRET_KEY")
    MEGABYTE = (2 ** 10) ** 2
    app.config['MAX_FORM_MEMORY_SIZE'] = 10 * MEGABYTE
    
    app.register_blueprint(errors_blueprint)
    app.register_blueprint(admin_blueprint, url_prefix="/admin")
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(main_blueprint)
    app.register_blueprint(home_blueprint, url_prefix="/home")
    
    return app