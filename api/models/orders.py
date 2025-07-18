from api.db import db

class Orders(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    client = db.Column(db.String())
    status = db.Column(db.String())
    date_entry = db.Column(db.DateTime)
    date_processed = db.Column(db.DateTime)
    products_list = db.relationship("OrderProducts", back_populates="order", cascade="all, delete-orphan")
