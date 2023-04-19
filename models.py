from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from uuid import uuid4
from datetime import datetime



class Layer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100))
    county = db.Column(db.String(100))
    folder = db.Column(db.String(100))
    service_name = db.Column(db.String(100))
    service_type = db.Column(db.String(100))
    layer_name = db.Column(db.String(100))
    geometry_type = db.Column(db.String(50))
    url = db.Column(db.String(1000), unique=True)
    is_active = db.Column(db.Boolean, default=False)
    data_points = db.relationship('DataPoint', backref='layer', lazy=True)
    primary_parcel_layer = db.Column(db.Boolean, default=False)


class Query(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid4()))
    address = db.Column(db.String(100))
    email = db.Column(db.String(100))
    data_points = db.relationship('DataPoint', backref='query', lazy=True)
    task_id = db.Column(db.String(100))
    city = db.Column(db.String(100))
    county = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('address', 'email', name='uix_field1_field2'),
    )


class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    properties = db.Column(db.JSON)
    geometry = db.Column(db.JSON)
    layer_id = db.Column(db.Integer, db.ForeignKey('layer.id'), nullable=False)
    query_id = db.Column(db.String(36), db.ForeignKey('query.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)







########### Tonic Prep

class TonicQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.Float)
    openai_text = db.Text()




