

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
import requests 
from models import db, Layer, Query
import os
from dotenv import load_dotenv



app = Flask(__name__)
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL_PARCELINI")
db.init_app(app)
migrate = Migrate(app, db)


def instances_to_json(instances):
    table_name = instances[0].__tablename__  # get the table name from the first instance
    data = {}
    for instance in instances:
        row_data = {}
        for column in instance.__table__.columns:
            row_data[column.name] = getattr(instance, column.name)
        data[instance.id] = row_data
    return jsonify(data)




@app.route('/')
def index():
    return 'Hello, world!'


@app.route('/layer', methods=['POST'])
def get_layer():
    city = request.form.get('city')
    layers = Layer.query.filter_by(city=city).all()
    # Process the list of layers as necessary
    if len(layers) > 0:
        return instances_to_json(layers)
    else:
        return make_response('', 204)
        
        


@app.route('/submit', methods=['POST'])
def submit_query():
    email = request.form['email']
    address = request.form['address']
    query = Query(email=email, address=address)
    db.session.add(query)
    db.session.commit()
    return 'Query submitted successfully!'



def traverse(root_link, city=None, folder_name = None, service_name = None, service_type = None):
    json_data = requests.get(root_link + '?f=json')
    data = json_data.json()
    if 'folders' in data.keys():
        for folder in data['folders']:
            traverse(root_link + '/' + folder, city=city, folder_name = folder)
    if 'services' in data.keys():
        for service in data['services']:
            if service['type'] in ['MapServer', 'FeatureServer']:
                traverse(root_link + '/' + service['name'] + '/' + service['type'], city=city, folder_name=folder_name, 
                         service_name = service['name'], service_type = service['type'])
    if 'layers' in data.keys():
        for layer in data['layers']:
            if 'geometryType' in layer.keys():
                print(root_link + '/' + str(layer['id']), city, service_name, service_type, layer['name'], layer['geometryType'])
                layer = Layer(city=city, folder=folder_name, service_name=service_name, 
                                    service_type=service_type,
                                    layer_name=layer['name'], geometry_type=layer['geometryType'], 
                                    url = root_link + '/' + service_name + '/' + service_type + '/'+ str(layer['id']))
                db.session.add(layer)
                db.session.commit()
                
            





if __name__ == '__main__':
    app.run(debug=True)
