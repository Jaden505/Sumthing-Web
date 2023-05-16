from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Proof(db.Model):
    __tablename__ = 'proof_table'
    proof_key = db.Column(db.Integer, primary_key=True)
    img_creation_date = db.Column(db.DateTime)
    img_name = db.Column(db.String, nullable=False)
    img_latitude = db.Column(db.Numeric(precision=20, scale=15))
    img_longitude = db.Column(db.Numeric(precision=20, scale=15))
    img_altitude = db.Column(db.Integer)
