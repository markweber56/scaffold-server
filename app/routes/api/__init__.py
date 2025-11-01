from flask import Blueprint, request
from functools import wraps
from sqlalchemy import text
# from flask.wrappers import Response
from flask_limiter import ExemptionScope
# from werkzeug.exceptions import HTTPException
# from flask_limiter.errors import RateLimitExceeded

# import logging

from app.extensions import limiter, csrf, redis_client
from app.utils.api import error_response, success_response
from app.utils.request_validators import Validator
from app.models.auth import User
# from app.utils.cache import get_cached_response, set_cached_response

api_bp = Blueprint("api", __name__, url_prefix="/api")
limiter.exempt(
    api_bp,
    flags=ExemptionScope.DEFAULT
    | ExemptionScope.APPLICATION
    | ExemptionScope.DESCENDENTS,
)


def jwt_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request_is_valid = Validator('api', request).validate()

        redis_val = redis_client.get("mykey")

        # TODO: finish this

        return f(*args, **kwargs)
    return decorated_function


@api_bp.route("/hello", methods=["GET"])
@limiter.limit("100 per day;10 per hour")
def test_api_hello():
    return success_response(message="Hello World!!")


@limiter.limit("100 per day;10 per hour")
@api_bp.route("/data", methods=["GET"])
def get_data():
    return success_response(data={'a': 1, 'b': 2}, message="here's some data")


@limiter.limit("100 per day;10 per hour")
@api_bp.route("/users", methods=["GET"])
def get_users():

    return_users = []
    users = User.query.all()

    for user in users:
        return_users.append({'first_name': user.first_name, 'last_name': user.last_name})
        print(f'user: {user.first_name} {user.last_name}')

    return success_response(data={'users': return_users})


@limiter.limit("100 per day;10 per hour")
@api_bp.route('/test', methods=["POST"])
@jwt_auth
def signup_user():
    return success_response(message="Whaddddddup")