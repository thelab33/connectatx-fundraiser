from app import db

class FooBar(db.Model):
    __tablename__='foo_bars'
    id=db.Column(db.Integer, primary_key=True)
