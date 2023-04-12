from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from uuid import uuid4




class Layer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100))
    folder = db.Column(db.String(100))
    service_name = db.Column(db.String(100))
    service_type = db.Column(db.String(100))
    layer_name = db.Column(db.String(100))
    geometry_type = db.Column(db.String(50))
    url = db.Column(db.String(1000))
    is_active = db.Column(db.Boolean, default=False)
    data_points = db.relationship('DataPoint', backref='layer', lazy=True)


class Query(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid4()))
    address = db.Column(db.String(100))
    email = db.Column(db.String(100))
    data_points = db.relationship('DataPoint', backref='query', lazy=True)


class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    properties = db.Column(db.JSON)
    layer_id = db.Column(db.Integer, db.ForeignKey('layer.id'), nullable=False)
    query_id = db.Column(db.String(36), db.ForeignKey('query.id'), nullable=False)










