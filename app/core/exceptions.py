from flask import jsonify
from werkzeug.exceptions import HTTPException

class APIError(HTTPException):
    """Clase base para errores de la API"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv

# Errores específicos
class DatabaseError(APIError):
    """Error relacionado con la base de datos"""
    def __init__(self, message="Error de base de datos"):
        super().__init__(message, 500)

class ValidationError(APIError):
    """Error de validación de datos"""
    def __init__(self, message="Datos inválidos", errors=None):
        super().__init__(message, 400)
        self.errors = errors or {}

class NotFoundError(APIError):
    """Recurso no encontrado"""
    def __init__(self, message="Recurso no encontrado"):
        super().__init__(message, 404)

class AuthError(APIError):
    """Error de autenticación/autorización"""
    def __init__(self, message="No autorizado", status_code=401):
        super().__init__(message, status_code)

class ConflictError(APIError):
    """Conflicto (ej: recurso ya existe)"""
    def __init__(self, message="El recurso ya existe"):
        super().__init__(message, 409)

def register_error_handlers(app):
    """Registra manejadores de errores globales"""
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"message": "Endpoint no encontrado"}), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({"message": "Error interno del servidor"}), 500