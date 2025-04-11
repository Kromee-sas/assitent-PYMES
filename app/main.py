from flask import Flask
from flask_jwt_extended import JWTManager
from app.auth.routes import auth_blueprint
from app.nlp.routes import nlp_blueprint
from app.database.models import db

def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "your_secret_here"

    JWTManager(app)
    db.init_app(app)

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(nlp_blueprint)

    return app