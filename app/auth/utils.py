from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token

def hash_password(password):
    return pbkdf2_sha256.hash(password)

def verify_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)

def generate_token(identity):
    return create_access_token(identity=identity)