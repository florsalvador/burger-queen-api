from api.db import db

class Users(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String())
    email = db.Column(db.String())
    password = db.Column(db.String())

    def create(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def as_dict(self):
        return {
            "id": self.id,
            "role": self.role,
            "email": self.email,
            "password": self.password
        }
