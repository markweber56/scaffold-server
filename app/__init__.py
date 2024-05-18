# import os

from flask import Flask


def create_app(debug: bool = False): 
    app = Flask(__name__)

    app.app_context().push()

    from app.config.common import Config

    app.config.from_object(Config)

    # initialize app extensions
    from app.extensions import bcrypt, cors, csrf, db, limiter, login_manager, redis_client
    
    bcrypt.init_app(app)
    cors.init_app(app)
    # csrf.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    redis_client.init_app(app)

    # register models
    from app import models

    db.create_all()

    # register blueprints
    from app.routes import api_bp, auth_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    # apply csrf exemption to blueprint
    csrf.exempt(api_bp)
    csrf.exempt(auth_bp)

    # Global Ratelimit Checker
    # this is used because auto_check is set to 'False'
    app.before_request(lambda: limiter.check())

    return app
