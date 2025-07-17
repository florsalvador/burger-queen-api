from flask import Flask, request
from api.config import Config
from api.db import db
from api.models.orders import Orders
from api.models.products import Products
from api.models.users import Users
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    @app.route("/orders", methods=["GET"])
    def get_orders():
        orders = Orders.query.all()
        results = []
        for order in orders:
            info = {
                "id": order.id,
                "user_id": order.user_id,
                "client": order.client,
                "status": order.status,
                "data_entry": order.data_entry,
                "date_processed": order.date_processed
            }
            results.append(info)
        return {"orders": results}

    @app.route("/products", methods=["GET"])
    def get_products():
        products = Products.query.all()
        results = []
        for product in products:
            info = {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "image": product.image,
                "type": product.type,
                "date_entry": product.date_entry
            }
            results.append(info)
        return {"products": results}

    @app.route("/products", methods=["POST"])
    def create_products():
        if request.is_json:
            data = request.get_json()
            date_entry_str = data.get("date_entry")
            if date_entry_str:
                try:
                    date_entry = datetime.fromisoformat(date_entry_str)
                except ValueError:
                    return {"error": "Invalid date format. Use ISO format like '2024-07-16T12:00:00'"}, 400
            else:
                date_entry = None
            new_product = Products(
                name=data["name"],
                price=data["price"],
                image=data["image"],
                type=data["type"],
                date_entry=date_entry
            )
            db.session.add(new_product)
            db.session.commit()
            return {"message": f"Product {new_product.name} has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}, 400

    @app.route("/users", methods=["GET"])
    def get_users():
        users = Users.query.all()
        results = [
            {
                "id": user.id,
                "role": user.role,
                "email": user.email,
                "password": user.password
            } for user in users
        ]
        return {"users": results}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
