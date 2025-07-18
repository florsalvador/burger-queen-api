from api.db import db

class OrderProducts(db.Model):
    __tablename__ = "order_products"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order = db.relationship("Orders", back_populates="products_list")
    product = db.relationship("Products")
