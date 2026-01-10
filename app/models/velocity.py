from app.extensions import db


class Velocity(db.Model):
    __tablename__ = 'velocity'
    __table_args__ = {'schema': 'stock'}

    ticker = db.Column(db.String(5))
    utc_time = db.Column(db.DateTime(timezone=True), primary_key=True)
    price = db.Column(db.Float, nullable=False)
    v5 = db.Column(db.Float, nullable=False)
    v10 = db.Column(db.Float, nullable=False)
    v15 = db.Column(db.Float, nullable=False)
    v30 = db.Column(db.Float, nullable=False)