from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db


class Price(db.Model, ):
    __tablename__ = 'prices'
    __table_args__ = {'schema': 'stock'}

    ticker = db.Column(db.String(5), ForeignKey('stock.securities.ticker'), primary_key=True)
    utc_time = db.Column(db.DateTime(timezone=True), primary_key=True)
    price = db.Column(db.Float, nullable=False)

    security = relationship("Security", backref="prices")
