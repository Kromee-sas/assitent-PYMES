from flask import jsonify
from flask_jwt_extended import JWTManager
from .services import TokenService

def configure_jwt(jwt: JWTManager):
    """Configura los manejadores de eventos para JWT"""
    
    
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return TokenService.is_token_revoked(jti)
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'message': 'Token inválido o manipulado',
            'error': 'invalid_token'
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'La sesión ha expirado',
            'error': 'token_expired'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'message': 'Se requiere autenticación',
            'error': 'authorization_required'
        }), 401
