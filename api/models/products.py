from api.db import db

class Products(db.Model):
    __tablename__ = "products"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    price = db.Column(db.Integer)
    image = db.Column(db.String())
    type = db.Column(db.String())
    date_entry = db.Column(db.DateTime, nullable=True)

    def __init__(self, name, price, image, type, date_entry):
        self.name = name
        self.price = price
        self.image = image
        self.type = type
        self.date_entry = date_entry