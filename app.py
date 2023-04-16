

from flask import Flask, jsonify, request, make_response, url_for, render_template
from flask_migrate import Migrate
import requests 
from models import db, Layer, Query, DataPoint
import os
from dotenv import load_dotenv
from celery import Celery
import time
import uuid
from datetime import datetime
from flask_mail import Mail, Message
import csv

app = Flask(__name__)
load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL_PARCELINI")
app.config['MAIL_SERVER'] = os.environ.get("MAIL_SERVER")
app.config['MAIL_PORT'] = os.environ.get("MAIL_PORT")
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")


db.init_app(app)
migrate = Migrate(app, db)




mail = Mail(app)


# Configure Celery
celery = Celery(
    app.import_name,
    broker=os.environ['REDIS_URL'],
    backend=os.environ['REDIS_URL']
)


@celery.task(name='app.add_numbers')
def add(x: int, y: int) -> int:
    time.sleep(5)
    return x + y


# Define a route for testing
@app.route('/add/<int:param1>/<int:param2>')
def add(param1: int, param2: int) -> str:
    task = celery.send_task('app.add_numbers', args=[param1, param2], kwargs={})
    response = f"<a href='{url_for('check_task', task_id=task.id, external=True)}'>check status of {task.id} </a>"
    return response

@app.route('/check/<string:task_id>')
def check_task(task_id: str) -> str:
    for i in range(100):
        print(i)
        print("!"*1000)
    res = celery.AsyncResult(task_id)
    return res.state




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
    print('here')
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

    new_uuid = uuid.uuid4()
    
    created_at = datetime.now()

    query = Query(id=new_uuid, email=email, address=address, created_at=created_at)

    db.session.add(query)
    db.session.commit()

    task = celery.send_task('app.find_and_save_data_for_polygon_layers', args=[new_uuid], kwargs={})

    query = Query.query.filter_by(id=str(new_uuid)).first()
    query.task_id = task.id
    db.session.commit()
    

    return jsonify({'id': new_uuid, 'task_id': task.id}), 201



def generate_parcel_report(query_id):

    query = Query.query.filter_by(id=query_id).first()
    data_points = db.session.query(DataPoint, Layer).\
            join(Layer).\
            join(Query).\
            filter(Query.id == query_id).\
            all()
    data = {}
    if query.city in ['Los Angeles']:
        for data_point, layer in data_points:
            if layer.service_name not in data:
                data[layer.service_name] = {}

            if layer.layer_name not in data[layer.service_name]:
                data[layer.service_name][layer.layer_name] = []

            data[layer.service_name][layer.layer_name] = {}
            data[layer.service_name][layer.layer_name]['id'] = data_point.id
            print(data_point.properties.keys())
            if 'features' in data_point.properties and len(data_point.properties['features']) > 0:
                data[layer.service_name][layer.layer_name]['properties'] = data_point.properties['features'][0]['properties']
            data[layer.service_name][layer.layer_name]['url'] = layer.url
        return data
    
    if query.city in ['San Diego', 'San Jose']:
        for data_point, layer in data_points:
            if layer.folder not in data:
                data[layer.folder] = {}

            if layer.layer_name not in data[layer.folder]:
                data[layer.folder][layer.layer_name] = []

            data[layer.folder][layer.layer_name] = {}
            data[layer.folder][layer.layer_name]['id'] = data_point.id
            print(data_point.properties.keys())
            if 'features' in data_point.properties and len(data_point.properties['features']) > 0:
                data[layer.folder][layer.layer_name]['properties'] = data_point.properties['features'][0]['properties']
            data[layer.folder][layer.layer_name]['url'] = layer.url
        return data





@app.route('/parcel_report', methods=['POST'])
def parcel_report():
    query_id = request.form['query_id']
    # query = Query.query.filter_by(id=query_id).first()
    return generate_parcel_report(query_id)



@app.route('/parcel_report_template/<query_id>')
def parcel_report_template(query_id):
    data = generate_parcel_report(query_id)
    return render_template('report_1.html', city_data=data)

    






def traverse(root_link, city=None, folder_name = None, service_name = None, service_type = None):
    json_data = requests.get(root_link + '?f=json')
    try:
        data = json_data.json()
    except:
        data = {}
    if 'folders' in data.keys():
        for folder in data['folders']:
            traverse(root_link + '/' + folder, city=city, folder_name=folder)
    if 'services' in data.keys():
        for service in data['services']:
            print(folder_name, service)
            if service['type'] in ['MapServer', 'FeatureServer']:
                if folder_name is None:
                    print(root_link + '/' + service['name'] + '/' + service['type'])
                    traverse(root_link + '/' + service['name'] + '/' + service['type'], city=city, folder_name=folder_name, 
                             service_name = service['name'], service_type = service['type'])
                else:
                    link = (root_link + '/' + service['name'].split('/')[1] + '/' + service['type'])
                    traverse(link, city=city, folder_name=folder_name, 
                             service_name = service['name'], service_type = service['type'])
    if 'layers' in data.keys():
        for layer in data['layers']:
            if 'geometryType' in layer.keys():
                print(root_link + '/' + str(layer['id']), city, service_name, service_type, layer['name'], layer['geometryType'])
                layer = Layer(city=city, folder=folder_name, service_name=service_name, 
                                    service_type=service_type,
                                    layer_name=layer['name'], geometry_type=layer['geometryType'], 
                                    url = root_link + '/'+ str(layer['id']))
                db.session.add(layer)
                db.session.commit()
                

            

def get_polygon_for_lat_lng(layer_id, lat, lng):
    layer = Layer.query.filter_by(id=layer_id).first()
    url = layer.url
    arcgis_query = f'{url}/query?where=1%3D1&text=&objectIds=&time=&geometry={lng}%2C{lat}&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelWithin&relationParam=&outFields=*&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&having=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount=&queryByDistance=&returnExtentOnly=false&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters=&featureEncoding=esriDefault&f=geojson'
    print(arcgis_query)
    response = requests.get(arcgis_query)
    return response.json()


def geocode_address(address):
    GEOCODIO_API = os.environ.get("GEOCODIO_API")
    address = address.replace(' ', '+')
    url = f"https://api.geocod.io/v1.7/geocode?q={address}&api_key={GEOCODIO_API}"
    response = requests.get(url)
    data = response.json()
    location = data['results'][0]
    return location


def send_parcel_report_email(address, email):
    message = Message(f'We are preparing your report for {address}', 
                    sender='info@parcelini.com', 
                    recipients=[email])
    # message.body = 'This is a test email sent from Flask!'
    message.html = render_template('report-prep.html', address=address)
    mail.send(message)
    print("Sent")
    return 'Email sent!'



@celery.task(name='app.find_and_save_data_for_polygon_layers')
def find_and_save_data_for_polygon_layers(query_id):
    time.sleep(10)
    with app.app_context():

        print('here')
        query = Query.query.filter_by(id=query_id).first()
        result = geocode_address(query.address)

        print(result)

        city = result['address_components']['city']
        county = result['address_components']['county']
        lat = result["location"]["lat"]
        lng = result["location"]["lng"]

        print("Sending")
        send_parcel_report_email(query.address, query.email)


        print(city, lat, lng)


        query.city = city
        query.county = county
        db.session.commit()
        layers = Layer.query.filter(
            Layer.city == city,
            Layer.geometry_type == 'esriGeometryPolygon',
            Layer.is_active
        ).all()

        print(layers)

        for layer in layers:
            data = get_polygon_for_lat_lng(layer.id, lat, lng)
            data_point = DataPoint(properties=data, layer_id=layer.id, query_id=query_id)
            db.session.add(data_point)
            db.session.commit()

        


def scrape():
    with open('deep_links.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            city = row[0]
            link = row[1]
            if link:
                traverse(link, city)




if __name__ == '__main__':
    app.run(debug=True)
