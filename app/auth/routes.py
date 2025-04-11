from flask import Blueprint, request, jsonify
from app.database.models import db, User
from app.auth.utils import hash_password, verify_password, generate_token

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    email = data['email']
    password = hash_password(data['password'])
    company_id = data['company_id']

    # Check if user exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({"error": "Username or email already exists"}), 409

    try:
        user = User(username=username, email=email, password_hash=password, company_id=company_id)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and verify_password(data['password'], user.password_hash):
        token = generate_token(identity={"user_id": user.id, "company_id": user.company_id})
        return jsonify(access_token=token)
    return jsonify({"message": "Invalid credentials"}), 401