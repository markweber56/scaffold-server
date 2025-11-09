from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_limiter import ExemptionScope
from functools import wraps
from jwt.exceptions import DecodeError, ExpiredSignatureError

from app.extensions import limiter, redis_client
from app.utils.api import error_response, success_response, generate_jwt, decode_jwt
from app.utils.request_validators import Validator
from app.models import User

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
        request_json = request.get_json()
        email = request_json['email']
        password = request_json['password']
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


@auth_bp.route('/authenticate', methods=["POST"])
def authenticate():
    token = request.headers['Authorization'].split()[1]
    print(f'token {token}')
    try:
        data = decode_jwt(token)
    except DecodeError:
        return error_response(message="error decoding token")
    except ExpiredSignatureError:
        return error_response(message="Token has expired")

    user_id = data['user_id']
    user = User.query.get(user_id)
    if user:
        print(f'Found matching user {user.first_name} {user.last_name}')
        return success_response(message="yoooo", data={'authenticated': True})
    else:
        return error_response(message="S my D")


def require_auth(f):  #NOTE: similar is also defined in api blueprint
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return jsonify({"message": "Authorization header missing"}), 401  #TODO: update to return error_resopnse, update error response to have code as argument also put codes in class / enum
        try:
            token = auth_header.split()[1]  # Expect 'Bearer <token>'
        except IndexError:
            return jsonify({"message": "Invalid authorization header"}), 401
        try:
            data = decode_jwt(token)
        except DecodeError:
            return jsonify({"message": "Error decoding token"}), 401
        except ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401

        user_id = data['user_id']
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "Invalid user"}), 401

        # Attach the user info to the request context if needed
        request.user = user

        return f(*args, **kwargs)
    return decorated_function
