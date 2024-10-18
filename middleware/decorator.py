from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

# Custom decorator to check user roles
def role_required(required_role):
    def decorator(func):
        @wraps(func)
        @jwt_required()  # Ensures that a valid JWT token is present
        def wrapper(*args, **kwargs):
            # Get the current user's identity from the JWT token
            user = get_jwt_identity()

            # Check if the user's role matches the required role
            if user['role'] < required_role:
                return jsonify({'message': 'Access denied: Insufficient privileges.'}), 403
            
            # Proceed if the user has the required role
            return func(*args, **kwargs)
        return wrapper
    return decorator
