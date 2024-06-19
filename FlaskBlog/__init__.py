from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
app= Flask(__name__)
app.config["SECRET_KEY"]='9ae469ff11ebfaa337c39c61c8a274000f97271242914dc2fed7d715750fa633'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

bcrypt= Bcrypt(app)
db= SQLAlchemy(app)
login_manager= LoginManager(app)
login_manager.login_view= "login"
login_manager.login_message_category= "info"

from FlaskBlog import routes