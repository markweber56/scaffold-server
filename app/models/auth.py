from flask_login import UserMixin
from datetime import datetime

from app.extensions import db
from app.utils.models import generate_uuid
from .core import TimestampMixin


class User(db.Model, UserMixin, TimestampMixin):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth'}

    id = db.Column(
        db.String, primary_key=True, default=generate_uuid, unique=True, nullable=False
    )
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    
