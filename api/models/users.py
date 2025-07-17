from api.db import db

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