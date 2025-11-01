from app.extensions import db
from .core import TimestampMixin


class Security(db.Model, TimestampMixin):
    __tablename__ = 'securities'
    __table_args__ = {'schema': 'stock'}

    ticker = db.Column(db.String(5), primary_key=True, unique=True, nullable=False)
    security_name = db.Column(db.String(50), nullable=False)
    gics_sector = db.Column(db.String(50), nullable=False)
    gics_sub_industry = db.Column(db.String(100), nullable=False)
    headquarters_location = db.Column(db.String(50), nullable=False)
    date_added = db.Column(db.Date, nullable=False)
    cik = db.Column(db.Integer, nullable=False)
    year_founded = db.Column(db.Integer, nullable=False)