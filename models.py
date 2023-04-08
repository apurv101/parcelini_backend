from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()





class Layer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100))
    folder = db.Column(db.String(100))
    service_name = db.Column(db.String(100))
    service_type = db.Column(db.String(100))
    layer_name = db.Column(db.String(100))
    geometry_type = db.Column(db.String(50))
    url = db.Column(db.String(1000))


class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100))
    email = db.Column(db.String(100))



