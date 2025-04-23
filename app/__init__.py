from flask import Flask
from app.core.config import Config
from app.core.extensions import db, migrate, jwt, bcrypt
from app.core.exceptions import register_error_handlers
from app.modules.auth.jwt_config import configure_jwt
from app.modules.auth.routes import auth_bp

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
    
    #configurar los manejadores de eventos JWT
    configure_jwt(jwt)
    
    # Registrar blueprints
    
    app.register_blueprint(auth_bp)
    
    return app