from flask import Flask
from app.core.config import Config
from app.core.extensions import db, migrate, jwt, bcrypt
from app.core.exceptions import register_error_handlers

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Registrar blueprints
    from app.modules.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    
    return app