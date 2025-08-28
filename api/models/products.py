from api.db import db

class Products(db.Model):
    __tablename__ = "products"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    price = db.Column(db.Integer)
    image = db.Column(db.String())
    type = db.Column(db.String())
    date_entry = db.Column(db.DateTime, nullable=True)

    def create(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "image": self.image,
            "type": self.type,
            "dateEntry": self.date_entry
        }
