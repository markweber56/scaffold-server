from flask import Blueprint
from sqlalchemy import text
# from flask.wrappers import Response
from flask_limiter import ExemptionScope
# from werkzeug.exceptions import HTTPException
# from flask_limiter.errors import RateLimitExceeded

# import logging

# Local modules
from app.extensions import limiter
from app.utils.api import error_response, success_response
from app.models.auth import User
from app.extensions.db import db
# from app.utils.cache import get_cached_response, set_cached_response

api_bp = Blueprint("api", __name__, url_prefix="/api")
limiter.exempt(
    api_bp,
    flags=ExemptionScope.DEFAULT
    | ExemptionScope.APPLICATION
    | ExemptionScope.DESCENDENTS,
)


@api_bp.route("/hello", methods=["GET"])
def test_api_hello():
    return success_response(message="Hello World!!")

@api_bp.route("/users", methods=["GET"])
def get_users():

    print(db.session.__dict__)
    return_users = []
    users = User.query.all()
    # users = db.session.query(User).all()

    for user in users:
        return_users.append({'first_name': user.first_name, 'last_name': user.last_name})
        print(f'user: {user.first_name} {user.last_name}')
    
    return success_response(data={'users': return_users})