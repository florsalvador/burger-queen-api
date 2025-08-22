from flask import Flask, request, jsonify
from api.config import Config
from api.db import db
from api.models.orders import Orders
from api.models.products import Products
from api.models.users import Users
from datetime import datetime, timezone


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    @app.route("/orders", methods=["GET"])
    def get_orders():
        orders = Orders.query.all()
        return jsonify([order.as_dict() for order in orders]), 200
    
    @app.route("/orders", methods=["POST"])
    def create_order():
        data = request.get_json()
        required_fields = ["userId", "client", "status", "dateEntry", "products"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400
        try:
            date_entry = datetime.fromisoformat(data.get("dateEntry"))
        except ValueError:
            return jsonify({"error": "Invalid date format."}), 400
        try:
            new_order = Orders(
                user_id=data.get("userId"),
                client=data.get("client"),
                status=data.get("status"),
                date_entry=date_entry,
                date_processed=None
            )
            new_order.add_products(data["products"])
            new_order.create()
            return jsonify(new_order.as_dict()), 201
        except ValueError as ve:
            db.session.rollback()
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    @app.route("/orders/<int:id>", methods=["PATCH"])
    def modify_order(id):
        data = request.get_json()
        status = data.get("status")
        if not status:
            return jsonify({"error": "Missing 'status' field"}), 400
        allowed_statuses = {"canceled", "ready", "delivered"}
        if status not in allowed_statuses:
            return jsonify({"error": f"Status must be one of {allowed_statuses}"}), 400
        order = Orders.query.get(id)
        if not order:
            return jsonify({"error": f"Order {id} does not exist"}), 404
        try:
            order.status = status
            order.date_processed = datetime.now(timezone.utc)
            order.update()
            return jsonify(order.as_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
        
    @app.route("/orders/<int:id>", methods=["DELETE"])
    def delete_order(id):
        order = Orders.query.get(id)
        if not order:
            return jsonify({"error": f"Order {id} does not exist"}), 404
        try:
            response = order.as_dict()
            order.delete()
            return jsonify(response), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route("/products", methods=["GET"])
    def get_products():
        products = Products.query.all()
        return jsonify([product.as_dict() for product in products]), 200
        
    @app.route("/products", methods=["POST"])
    def create_product():
        data = request.get_json()
        required_fields = ["name", "price", "image", "type", "dateEntry"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400
        try:
            date_entry = datetime.fromisoformat(data.get("dateEntry"))
        except ValueError:
            return jsonify({"error": "Invalid date format."}), 400
        try:
            new_product = Products(
                name=data.get("name"),
                price=data.get("price"),
                image=data.get("image"),
                type=data.get("type"),
                date_entry=date_entry
            )
            new_product.create()
            return jsonify(new_product.as_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
        
    @app.route("/products/<int:id>", methods=["PATCH"])
    def modify_product(id):
        data = request.get_json()
        product = Products.query.get(id)
        if not product:
            return jsonify({"error": f"Product {id} does not exist"}), 404
        try:
            if "dateEntry" in data:
                try:
                    product.date_entry = datetime.fromisoformat(data.get("dateEntry"))
                except ValueError:
                    return jsonify({"error": "Invalid date format."}), 400
            if "name" in data:
                product.name = data["name"]
            if "price" in data:
                product.price = data["price"]
            if "image" in data:
                product.image = data["image"]
            if "type" in data:
                product.type = data["type"]
            product.update()
            return jsonify(product.as_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    @app.route("/products/<int:id>", methods=["DELETE"])
    def delete_product(id):
        product = Products.query.get(id)
        if not product:
            return jsonify({"error": f"Product {id} does not exist"}), 404
        try:
            response = product.as_dict()
            product.delete()
            return jsonify(response), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

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
