from flask import Flask, request, jsonify
from api.config import Config
from api.db import db
from api.models.orders import Orders
from api.models.products import Products
from api.models.users import Users
from datetime import datetime, timezone
from flask_jwt_extended import (
    create_access_token, 
    get_jwt_identity, 
    jwt_required, 
    JWTManager
)
from flask_bcrypt import Bcrypt
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt = JWTManager(app)
    bcrypt = Bcrypt(app)
    CORS(app, origins=["https://burger-queen-seven.vercel.app"])

    @app.route("/orders", methods=["GET"])
    @jwt_required()
    def get_orders():
        orders = Orders.query.all()
        return jsonify([order.as_dict() for order in orders]), 200
    
    @app.route("/orders", methods=["POST"])
    @jwt_required()
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
    @jwt_required()
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
    @jwt_required()
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
    @jwt_required()
    def get_products():
        products = Products.query.all()
        return jsonify([product.as_dict() for product in products]), 200
        
    @app.route("/products", methods=["POST"])
    @jwt_required()
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
    @jwt_required()
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
    @jwt_required()
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
    @jwt_required()
    def get_users():
        users = Users.query.all()
        return jsonify([user.as_dict() for user in users]), 200
    
    @app.route("/users", methods=["POST"])
    @jwt_required()
    def create_user():
        current_user = get_jwt_identity()
        current_user_data = Users.query.get(current_user)
        if current_user_data.role != "admin":
            return jsonify({"error": "Only admins can create users"}), 403
        data = request.get_json()
        required_fields = ["role", "email", "password"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400
        user = Users.query.filter(Users.email == data.get("email")).first()
        if user:
            return jsonify({"error": "User already exists"}), 409
        try:
            new_user = Users(
                role=data.get("role"),
                email=data.get("email"),
                password=bcrypt.generate_password_hash(data.get("password")).decode("utf-8")
            )
            new_user.create()
            return jsonify(new_user.as_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
        
    @app.route("/users/<int:id>", methods=["PATCH"])
    @jwt_required()
    def modify_user(id):
        current_user = get_jwt_identity()
        current_user_data = Users.query.get(current_user)
        if current_user_data.role != "admin":
            return jsonify({"error": "Only admins can modify users"}), 403
        data = request.get_json()
        user = Users.query.get(id)
        if not user:
            return jsonify({"error": f"User does not exist"}), 404
        try:
            if "role" in data:
                user.role = data["role"]
            if "email" in data:
                user.email =  data["email"]
            if "password" in data:
                user.password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
            user.update()
            return jsonify(user.as_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
        
    @app.route("/users/<int:id>", methods=["DELETE"])
    @jwt_required()
    def delete_user(id):
        current_user = get_jwt_identity()
        current_user_data = Users.query.get(current_user)
        if current_user_data.role != "admin":
            return jsonify({"error": "Only admins can delete users"}), 403
        user = Users.query.get(id)
        if not user:
            return jsonify({"error": "User does not exist"}), 404
        try:
            response = user.as_dict()
            user.delete()
            return jsonify(response), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
        
    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json()
        try:
            email = data["email"]
            password = data["password"]
        except KeyError:
            return jsonify({"error": "Missing email or password"}), 400
        user = Users.query.filter(Users.email == email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=str(user.id))
            response = {
                "accessToken": access_token,
                "user": {"id": user.id, "email": user.email}
            }
            return jsonify(response), 200
        return jsonify({"error": "Email or password incorrect"}), 401
    
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run()
