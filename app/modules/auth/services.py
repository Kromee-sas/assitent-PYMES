from datetime import datetime

from app.core.extensions import db, bcrypt  
from flask_jwt_extended import create_access_token, create_refresh_token

from app.core.exceptions import (
    ValidationError, 
    AuthError, 
    ConflictError, 
    DatabaseError
)
from .models import Usuario
from .schemas import UsuarioSchema, LoginSchema

class AuthService:
    @staticmethod
    def hash_password(password):
        """Hashea una contraseña"""
        return bcrypt.generate_password_hash(password).decode('utf-8')

    @staticmethod
    def verify_password(password_hash, password):
        """Verifica una contraseña contra su hash"""
        return bcrypt.check_password_hash(password_hash, password)

    @staticmethod
    def update_user_login(user):
        """Actualiza el último login del usuario"""
        user.last_login = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
    
    @staticmethod
    def registrar_usuario(data):
        schema = UsuarioSchema()
        errors = schema.validate(data)
        if errors:
            raise ValidationError("Datos inválidos", errors=errors)
        
        if Usuario.query.filter_by(email=data['email']).first():
            raise ConflictError("El email ya está registrado")

        try:
            nuevo_usuario = Usuario(
                nombre=data['nombre'],
                email=data['email'],
                password=data['password'],
                rol=data.get('rol', 'empleado'),
                nivel_acceso=data.get('nivel_acceso', 1)
            )
            nuevo_usuario.save()
            return schema.dump(nuevo_usuario)
        except Exception as e:
            raise DatabaseError(f"Error al registrar usuario: {str(e)}")

    @staticmethod
    def login_usuario(data):
        schema = LoginSchema()
        errors = schema.validate(data)
        if errors:
            raise ValidationError("Datos inválidos", errors=errors)

        usuario = Usuario.query.filter_by(email=data['email']).first()
                
        if not usuario or not AuthService.verify_password(usuario.password_hash, data['password']):
            raise AuthError("Email o contraseña incorrectos")

        if not usuario.estado:
            raise AuthError("Cuenta desactivada", 403)

        AuthService.update_user_login(usuario)  # Usa el método estático existente
        
        return {
            "access_token": create_access_token(identity=str(usuario.id)),
            "refresh_token": create_refresh_token(identity=str(usuario.id)),
            "usuario": UsuarioSchema().dump(usuario)
        }

   