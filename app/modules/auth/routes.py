from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .services import AuthService
from app.core.exceptions import APIError , ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token



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


