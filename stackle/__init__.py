from os.path import abspath, dirname, join
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


# Initialize flask app
app = Flask(__name__)

# Configurations
# Configure flask app
app.config['SECRET_KEY'] = 'somesecretkey'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DB_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/stackle'; 


UPLOAD_FOLDER = join(abspath(dirname(__file__)), join('static', 'images'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize flask-sqlalchemy
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Login before you proceed'
login_manager.login_message_category = 'info'

bcrypt = Bcrypt(app)


from stackle import routes