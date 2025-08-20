from flask import Flask, request, jsonify
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
        return jsonify([order.as_dict() for order in orders]), 200
    
    @app.route("/orders", methods=["POST"])
    def create_orders():
        data = request.get_json()
        try:
            new_order = Orders(
                user_id=data.get("userId"),
                client=data.get("client"),
                status=data.get("status"),
                date_entry=datetime.fromisoformat(data.get("dateEntry")),
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
    def modify_orders(id):
        data = request.get_json()
        order = Orders.query.get(id)
        if not order:
            return jsonify({"error": f"Order {id} does not exist"}), 404
        status = data.get("status")
        date_processed = data.get("dateProcessed")
        if not status or not date_processed:
            return jsonify({"error": "Both 'status' and 'dateProcessed' are required."}), 400
        try:
            order.status = status
            order.date_processed = datetime.fromisoformat(date_processed)
            order.update()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
        return jsonify(order.as_dict()), 200
        
    @app.route("/orders/<int:id>", methods=["DELETE"])
    def delete_orders(id):
        order = Orders.query.get(id)
        if not order:
            return jsonify({"error": f"Order {id} does not exist"}), 404
        try:
            order.delete()
            return jsonify({"message": f"Order {id} deleted successfully"}), 200
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
