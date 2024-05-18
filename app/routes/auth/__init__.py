import jwt

from flask import Blueprint, request
from flask_bcrypt import Bcrypt
from flask_limiter import ExemptionScope

from app.config.common import Config
from app.extensions import limiter, redis_client
from app.utils.api import error_response, success_response, generate_jwt, decode_jwt
from app.utils.request_validators import Validator
from app.models.auth import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
limiter.exempt(
    auth_bp,
    flags=ExemptionScope.DEFAULT
    | ExemptionScope.APPLICATION
    | ExemptionScope.DESCENDENTS,
)
bcrypt = Bcrypt()

@auth_bp.route('/signup', methods=["POST"])
def signup_user():
    print(f"request: {request.__dict__}")
    return success_response(message="Whaddddddup")


@auth_bp.route('/login', methods=['POST'])
def login():
    request_is_valid = Validator('auth/login', request).validate()

    if request_is_valid:
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user is None:
            return error_response(message=f'Account for email address {email} not found')
        
        valid_password = bcrypt.check_password_hash(user.password_hash, password)
        if not valid_password:
            return error_response('Incorrect password')
        
        user_id = user.id
        jwt_token = generate_jwt(user_id)

        redis_client.set(user_id, jwt_token)

        response_message = f"you're logged in: {user.first_name} {user.last_name}"
        response_data = {
            'user_id': user_id,
            'token': jwt_token
        }
        
        return success_response(
            message=response_message,
            data=response_data
        )
    
    return error_response(message="Invalid request")