# routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import User
from db import db

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 1)

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = User(email=email)
    new_user.set_password(password)
    new_user.set_role(role)  

    db.session.add(new_user)
    db.session.commit()

    # return jsonify({"email": email}), 200
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity={'email': user.email})

        if user.role == 2:
            return jsonify(access_token=access_token, role=user.role, id=user.id, doctor_id=user.doctor_id), 200
        
        if user.role == 3:
            return jsonify(access_token=access_token, role=user.role, id=user.id, patient_id=user.patient_id), 200
        else:
            return jsonify(access_token=access_token, role=user.role, id=user.id), 200
            
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@auth_bp.route('/users', methods=['GET'])
def users():
    user_count = User.query.count()
    return jsonify(user_count=user_count), 200
