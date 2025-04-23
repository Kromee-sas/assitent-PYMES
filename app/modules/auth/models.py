from datetime import datetime
from app.core.extensions import db, bcrypt  
from app.core.database import BaseModel

class Usuario(BaseModel):
    __tablename__ = 'usuarios'
    
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='empleado')
    nivel_acceso = db.Column(db.Integer, nullable=False, default=1)
    estado = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)

    

    def __repr__(self):
        return f'<Usuario {self.email}>'
    
class TokenBlacklist(BaseModel):
    __tablename__ = 'token_blacklist'
    
    jti = db.Column(db.String(36), nullable=False, index=True)
    token_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    expires_at = db.Column(db.DateTime, nullable=False)
    
    usuario = db.relationship('Usuario', backref=db.backref('tokens_revocados', lazy='dynamic'))
    
    def __repr__(self):
        return f'<TokenBlacklist {self.jti}>'
    

    
    
