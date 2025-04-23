from marshmallow import Schema, fields, validate, validates_schema

class UsuarioSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    rol = fields.Str(validate=validate.OneOf(['superadmin', 'administrador', 'empleado']))
    nivel_acceso = fields.Int(validate=validate.OneOf([1, 2, 3]))
    estado = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_nivel_acceso(self, data, **kwargs):
        if 'rol' in data and 'nivel_acceso' in data:
            rol = data['rol']
            nivel = data['nivel_acceso']
            if rol == 'superadmin' and nivel != 3:
                raise validate.ValidationError("Nivel de acceso debe ser 3 para superadmin")
            elif rol == 'administrador' and nivel != 2:
                raise validate.ValidationError("Nivel de acceso debe ser 2 para administrador")
            elif rol == 'empleado' and nivel != 1:
                raise validate.ValidationError("Nivel de acceso debe ser 1 para empleado")

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)