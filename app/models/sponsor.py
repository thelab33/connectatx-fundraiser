from app import db

class Sponsor(db.Model):
    __tablename__ = "sponsors"

    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(100), nullable=False)

    # Fields used in main.py
    amount  = db.Column(db.Integer, default=0)        # cents or pennies
    status  = db.Column(db.String(32), default="pending")
    deleted = db.Column(db.Boolean, default=False)
