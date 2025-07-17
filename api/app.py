from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

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

if __name__ == "__main__":
    app.run(debug=True)
