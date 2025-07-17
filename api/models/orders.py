from api.db import db

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