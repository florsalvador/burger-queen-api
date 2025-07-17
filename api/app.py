from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Orders(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    client = db.Column(db.String())
    status = db.Column(db.String())
    data_entry = db.Column(db.DateTime)
    date_processed = db.Column(db.DateTime)
    def __init__(self, user_id, client, status, data_entry, date_processed):
        self.user_id = user_id
        self.client = client
        self.status = status
        self.data_entry = data_entry
        self.date_processed = date_processed

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

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String())
    email = db.Column(db.String())
    password = db.Column(db.String())
    def __init__(self, role, email, password):
        self.role = role
        self.email = email
        self.password = password

@app.route("/")
def index():
    return "Index"

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

if __name__ == "__main__":
    app.run(debug=True)
