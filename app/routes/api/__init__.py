from flask import Blueprint, jsonify, request
from flask_limiter import ExemptionScope
from functools import wraps
from jwt.exceptions import DecodeError, ExpiredSignatureError
from sqlalchemy import text, func, cast, Date

from app.extensions import limiter, csrf, redis_client
from app.utils.api import decode_jwt, error_response, success_response
from app.utils.request_validators import Validator
from app.models import Price, Security, User, Velocity
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
        # request_is_valid = Validator('api', request).validate()
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return jsonify({"message": "Authorization header missing"}), 401  # TODO: update to return error_response, update error response to have code as argument also put codes in class / enum
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

        return f(*args, **kwargs)
    return decorated_function


@api_bp.route("/hello", methods=["GET"])
@limiter.limit("100 per day;10 per hour")
def test_api_hello():
    return success_response(message="Hello World!!")


@limiter.limit("100 per day;10 per hour")
@api_bp.route("/data", methods=["GET"])
@jwt_auth
def get_data():
    return success_response(data={'a': 1, 'b': 2}, message="here's some data")


@api_bp.route("/tickers", methods=["GET"])
@limiter.limit("10000 per day;10000 per hour")
@jwt_auth
def get_tickers():
    tickers = [s.ticker for s in Security.query.all()]
    return success_response(data={'tickers': tickers})


@api_bp.route("/available-dates", methods=["GET"])
@limiter.limit("10000 per day; 10000 per hour")
@jwt_auth
def get_available_dates():
    ticker = request.args.get('ticker')

    dates_query = Price.query.filter(Price.ticker == ticker).with_entities(
        func.date(Price.utc_time).label('date')
    ).distinct().order_by(func.date(Price.utc_time))

    dates = [str(d.date) for d in dates_query.all()]

    return success_response(data={'dates': dates})


@api_bp.route("/ticker-data", methods=["GET"])
@limiter.limit("10000 per day; 10000 per hour")
@jwt_auth
def get_ticker_data():
    ticker = request.args.get('ticker')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Velocity.query.filter(Velocity.ticker == ticker)

    if start_date:
        query = query.filter(Velocity.utc_time >= start_date)
    if end_date:
        query = query.filter(Velocity.utc_time <= end_date + ' 23:59:59')

    query_data = query.order_by(Velocity.utc_time).all()

    data = [[qd.utc_time.isoformat(), qd.price, qd.v30] for qd in query_data]

    return success_response(message=f"data for {ticker}", data=data)


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