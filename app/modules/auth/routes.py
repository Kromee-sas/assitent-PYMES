from flask import Blueprint, request, jsonify
from .services import AuthService
from app.core.exceptions import APIError , ValidationError, AuthError
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, get_jwt

from datetime import datetime, timezone
from .services import TokenService



auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            raise APIError("Se esperaba un JSON", 400)

        # Validar campos obligatorios
        required_fields = ['nombre', 'email', 'password', 'rol', 'nivel_acceso']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Campo requerido faltante: {field}")

        usuario = AuthService.registrar_usuario(data)
        return jsonify({
            "message": "Usuario registrado exitosamente",
            "usuario": usuario
        }), 201
        
    except APIError as e:
        return jsonify({"error": e.message, "details": getattr(e, 'errors', None)}), e.status_code

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            raise APIError("Se esperaba un JSON", 400)
            
        tokens = AuthService.login_usuario(data)
        return jsonify(tokens), 200
        
    except APIError as e:
        return jsonify({"error": e.message}), e.status_code
    


@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    try:
        identidad = get_jwt_identity()  # El usuario original del refresh_token
        nuevo_token = create_access_token(identity=identidad)
        
        return jsonify({
            'access_token': nuevo_token,
            'message': 'Nuevo token generado exitosamente'
        }), 200
    except Exception as e:
        return jsonify({"error": "Error al refrescar el token", "details": str(e)}), 500
    


@auth_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Cierra la sesión actual (revoca el token actual)"""
    try:
        token = get_jwt()
        jti = token['jti']
        user_id = get_jwt_identity()
        
        # Guardar token en lista negra
        TokenService.revoke_token(
            jti=jti,
            user_id=user_id,
            expires_at=datetime.fromtimestamp(token['exp'], timezone.utc)
        )
        
        # Limpiar tokens expirados (mantenimiento)
        TokenService.cleanup_expired_tokens()
        
        return jsonify({
            "message": "Sesión cerrada correctamente"
        }), 200
    except Exception as e:
        return jsonify({"error": "Error al cerrar sesión", "details": str(e)}), 500

@auth_bp.route('/auth/logout/all', methods=['POST'])
@jwt_required()
def logout_all_sessions():
    """Cierra todas las sesiones del usuario (revoca todos los tokens)"""
    try:
        current_token = get_jwt()
        user_id = get_jwt_identity()        
        user_role = current_token.get('user_role')
        access_level = current_token.get('access_level')
        
        if user_role != 'superadmin' or access_level != 3:
            raise AuthError("No tienes permisos para realizar esta acción", 403)
        
        # Obtener todos los usuarios activos
        active_users = AuthService.get_all_active_users()
        session_count = 0 # Contador de sesiones cerradas
        
        # Revocar todas las sesiones de todos los usuarios
        for user in active_users:
            # Revocar tokens activos del usuario
            tokens = TokenService.get_user_active_tokens(user.id)
            session_count += len(tokens)
            
            # Añadir todos los tokens a la lista negra
            for token in tokens:
                TokenService.revoke_token(
                    jti=token.jti,
                    user_id=token.user_id,
                    expires_at=token.expires_at,
                    token_type=token.token_type
                )
        
        # Revocar el token actual también
        TokenService.revoke_token(
            jti=current_token['jti'],
            user_id=user_id,
            expires_at=datetime.fromtimestamp(current_token['exp'], timezone.utc)
        )
        session_count += 1
        
        # Limpiar tokens expirados (mantenimiento)
        TokenService.cleanup_expired_tokens()
        
        return jsonify({
            "message": f"Se cerraron {session_count} sesiones de todos los usuarios correctamente"
        }), 200
    except AuthError as e:
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        return jsonify({"error": "Error al cerrar todas las sesiones", "details": str(e)}), 500
    
@auth_bp.route('/auth/list-users', methods=['GET'])
@jwt_required()
def list_users():
    try:
        current_token = get_jwt()
        user_role = current_token.get('user_role')        
        usuarios = AuthService.filtrar_usuarios_por_rol(user_role)        
        return jsonify({
            "success": True,
            "count": len(usuarios),
            "users": usuarios,
            "your_role": user_role
        }), 200
        
    except AuthError as e:
        return jsonify({"success": False, "error": e.message}), e.status_code
    except Exception as e:
        return jsonify({"success": False, "error": "Error interno"}), 500


