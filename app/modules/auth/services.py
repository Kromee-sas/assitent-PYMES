from datetime import datetime, timezone
from app.core.extensions import db, bcrypt  
from flask_jwt_extended import create_access_token, create_refresh_token
from app.core.exceptions import (
    ValidationError, 
    AuthError, 
    ConflictError, 
    DatabaseError
)
from .models import Usuario, TokenBlacklist
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
                password_hash=AuthService.hash_password(data['password']),
                rol=data.get('rol', 'empleado'),
                nivel_acceso=data.get('nivel_acceso', 1)
            )
            nuevo_usuario.save()
            return schema.dump(nuevo_usuario)
        except Exception as e:
            raise DatabaseError(f"Error al registrar usuario: {str(e)}")
        
    @staticmethod
    def get_all_active_users():
        """Obtiene todos los usuarios activos del sistema"""
        usuarios = Usuario.query.filter_by(estado=True).all()
        return UsuarioSchema(many=True).dump(usuarios)

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

        additional_claims = {
        "user_role": usuario.rol,
        "access_level": usuario.nivel_acceso,
        "email": usuario.email,
        
        }
        AuthService.update_user_login(usuario)  # Usa el método estático existente
        
        return {
            "access_token": create_access_token(identity=str(usuario.id),additional_claims=additional_claims),
            "refresh_token": create_refresh_token(identity=str(usuario.id),additional_claims=additional_claims),
            "usuario": UsuarioSchema().dump(usuario)
        }
        
        
        
    @staticmethod
    def get_active_sessions(user_id):
        """Obtiene información sobre todas las sesiones activas del usuario"""
            
        # Obtener tokens no revocados
        now = datetime.now(timezone.utc)
        tokens_revocados = set(t.jti for t in TokenBlacklist.query.filter_by(user_id=user_id).all())        
        # SE podria almacenar metadatos de sesión (dispositivo, IP, etc.)        
        return [] 
    
    
    @staticmethod
    def filtrar_usuarios_por_rol(rol_usuario):
        """Filtra usuarios según el rol del usuario actual"""
        if not rol_usuario:
            raise AuthError("Rol no especificado", 400)
        
        query = Usuario.query.filter_by(estado=True)  # Solo usuarios activos
        
        if rol_usuario == 'superadmin':
            usuarios = query.all()
        elif rol_usuario == 'administrador':
            usuarios = query.filter(Usuario.rol.in_(['empleado', 'administrador'])).filter(Usuario.nivel_acceso <= 2).all()
        elif rol_usuario == 'empleado':
            usuarios = query.filter_by(rol='empleado', nivel_acceso=1).all()
        else:
            raise AuthError("Rol no válido", 403)        
        # Serialización automática
        return UsuarioSchema(many=True).dump(usuarios)
        
        
        
         

class TokenService:
    @staticmethod
    def revoke_token(jti, user_id, expires_at, token_type='access'):
        """Registra un token en la lista negra"""
        token = TokenBlacklist(
            jti=jti,
            user_id=user_id,
            token_type=token_type,
            expires_at=expires_at
        )
        token.save()
    
    @staticmethod
    def is_token_revoked(jti):
        """Verifica si un token está en la lista negra"""
        return TokenBlacklist.query.filter_by(jti=jti).first() is not None
    
    @staticmethod
    def get_user_active_tokens(user_id):
        """Obtiene todos los tokens activos de un usuario"""
        now = datetime.now(timezone.utc)
        return TokenBlacklist.query.filter(
            TokenBlacklist.user_id == user_id,
            TokenBlacklist.expires_at > now
        ).all()
    
    @staticmethod
    def cleanup_expired_tokens():
        """Elimina los tokens expirados de la base de datos"""
        now = datetime.now(timezone.utc)
        try:
            expired_tokens = TokenBlacklist.query.filter(TokenBlacklist.expires_at < now).delete()
            db.session.commit()
            return expired_tokens
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Error limpiando tokens expirados: {str(e)}")
    @staticmethod
    def get_user_active_tokens(user_id):
        """Obtiene todos los tokens activos de un usuario que NO están en la lista negra"""
        now = datetime.now(timezone.utc)
        return TokenBlacklist.query.filter(
            TokenBlacklist.user_id == user_id,
            TokenBlacklist.expires_at > now
        ).all()

   