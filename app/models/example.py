from app import db

class Example(db.Model):
    __tablename__='examples'
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(120))
