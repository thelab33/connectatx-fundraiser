from app import db

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id          = db.Column(db.Integer, primary_key=True)
    amount_cents= db.Column(db.Integer)
