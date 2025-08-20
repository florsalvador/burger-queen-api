from api.db import db
from api.models.products import Products
from api.models.order_products import OrderProducts

class Orders(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    client = db.Column(db.String())
    status = db.Column(db.String())
    date_entry = db.Column(db.DateTime)
    date_processed = db.Column(db.DateTime)
    products_list = db.relationship("OrderProducts", back_populates="order", cascade="all, delete-orphan")

    def create(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def as_dict(self):
        order_info = {
            "id": self.id,
            "userId": self.user_id,
            "client": self.client,
            "status": self.status,
            "dateEntry": self.date_entry,
            "dateProcessed": self.date_processed,
            "products": []
        }
        for prod in self.products_list:
            order_info["products"].append({
                "qty": prod.quantity,
                "product": {
                    "id": prod.product.id,
                    "name": prod.product.name,
                    "price": prod.product.price,
                    "image": prod.product.image,
                    "type": prod.product.type,
                    "dateEntry": prod.product.date_entry
                }
            })
        return order_info

    def add_products(self, products_data):
        for item in products_data:
            product_id = item["product"]["id"]
            quantity = item["qty"]
            product = Products.query.get(product_id)
            if not product:
                raise ValueError(f"Product id {product_id} does not exist")
            order_product = OrderProducts(
                product_id=product_id,
                quantity=quantity
            )
            self.products_list.append(order_product)
