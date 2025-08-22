from app import db

class FooModel(db.Model):
    __tablename__='foo_models'
    id=db.Column(db.Integer, primary_key=True)
