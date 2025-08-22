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
        results = []
        for product in products:
            info = {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "image": product.image,
                "type": product.type,
                "dateEntry": product.date_entry
            }
            results.append(info)
        return {"products": results}

    @app.route("/products", methods=["POST"])
    def create_products():
        if request.is_json:
            data = request.get_json()
            date_entry_str = data.get("dateEntry")
            if date_entry_str:
                try:
                    date_entry = datetime.fromisoformat(date_entry_str)
                except ValueError:
                    return {"error": "Invalid date format."}, 400
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
