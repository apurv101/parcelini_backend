

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
import pdfkit
import boto3
import platform, subprocess
import sys
import openai
import re
import json
from flask_cors import CORS
import sqlalchemy


app = Flask(__name__)
CORS(app)
load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL_PARCELINI")
app.config['MAIL_SERVER'] = os.environ.get("MAIL_SERVER")
app.config['MAIL_PORT'] = os.environ.get("MAIL_PORT")
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")


openai.api_key = os.environ.get("OPENAI_KEY")



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

###############################################################################################


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
    

def _get_pdfkit_config():
     """wkhtmltopdf lives and functions differently depending on Windows or Linux. We
      need to support both since we develop on windows but deploy on Heroku.

     Returns:
         A pdfkit configuration
     """
     if platform.system() == 'Windows':
         return pdfkit.configuration(wkhtmltopdf=os.environ.get('WKHTMLTOPDF_BINARY', 'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'))
     else:
         WKHTMLTOPDF_CMD = subprocess.Popen(['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf')], stdout=subprocess.PIPE).communicate()[0].strip()
         return pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)
     

def make_pdf_from_raw_html(html, options=None):
    """Produces a pdf from raw html.
    Args:
        html (str): Valid html
        options (dict, optional): for specifying pdf parameters like landscape
            mode and margins
    Returns:
        pdf of the supplied html
    """
    return pdfkit.from_string(html, False, configuration=_get_pdfkit_config(), options=options)
    
        

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
    
    data = []
    for data_point, layer in data_points:
        data_attribute = {}
        data_attribute["folder"] = layer.folder
        data_attribute["service_name"] = layer.service_name
        data_attribute["layer_name"] = layer.layer_name
        data_attribute["url"] = layer.url
        if 'features' in data_point.properties and len(data_point.properties['features']) > 0:
            data_attribute['properties'] = data_point.properties['features'][0]['properties']
        data.append(data_attribute)
    return data
    

    """
    data = {}
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
    """
    




@app.route('/parcel_report', methods=['POST'])
def parcel_report():
    query_id = request.form['query_id']
    # query = Query.query.filter_by(id=query_id).first()
    return generate_parcel_report(query_id)



@app.route('/parcel_report_template/<query_id>')
def parcel_report_template(query_id):
    data = generate_parcel_report(query_id)
    return render_template('general_report.html', layers=data)

    






def traverse(root_link, city=None, county=None, folder_name = None, service_name = None, service_type = None):
    json_data = requests.get(root_link + '?f=json')
    try:
        data = json_data.json()
    except:
        data = {}
    if 'folders' in data.keys():
        for folder in data['folders']:
            traverse(root_link + '/' + folder, city=city, county=county, folder_name=folder)
    if 'services' in data.keys():
        for service in data['services']:
            print(folder_name, service)
            if service['type'] in ['MapServer', 'FeatureServer']:
                if folder_name is None:
                    print(root_link + '/' + service['name'] + '/' + service['type'])
                    traverse(root_link + '/' + service['name'] + '/' + service['type'], city=city, county=county, folder_name=folder_name, 
                             service_name = service['name'], service_type = service['type'])
                else:
                    link = (root_link + '/' + service['name'].split('/')[1] + '/' + service['type'])
                    traverse(link, city=city, county=county, folder_name=folder_name, 
                             service_name = service['name'], service_type = service['type'])
    if 'layers' in data.keys():
        for layer in data['layers']:
            if 'geometryType' in layer.keys():
                print(root_link + '/' + str(layer['id']), city, service_name, service_type, layer['name'], layer['geometryType'])
                layer = Layer(city=city, county=county, folder=folder_name, service_name=service_name, 
                                    service_type=service_type,
                                    layer_name=layer['name'], geometry_type=layer['geometryType'], 
                                    url = root_link + '/'+ str(layer['id']))
                try:
                    db.session.add(layer)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Transaction rolled back due to exception: {e}")



            

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

def send_complete_parcel_report_email(address, email, href):
    message = Message(f'Your report for {address} is ready', 
                    sender='info@parcelini.com', 
                    recipients=[email])
    # message.body = 'This is a test email sent from Flask!'
    message.html = render_template('report-complete.html', address=address, href=href)
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
            Layer.geometry_type == 'esriGeometryPolygon'
        ).all()

        print(layers)

        for layer in layers:
            data = get_polygon_for_lat_lng(layer.id, lat, lng)
            data_point = DataPoint(properties=data, layer_id=layer.id, query_id=query_id)
            db.session.add(data_point)
            db.session.commit()

        


        
        
                    
        html = parcel_report_template(query_id)


        if sys.platform == "darwin":
            pdfkit.from_string(html, f'{query_id}.pdf')
        else:
            config = pdfkit.configuration(wkhtmltopdf='bin/wkhtmltopdf')
            options = {
                'page-size': 'A4',
                'encoding': "UTF-8",
                'zoom': '0.8'
            }
            pdfkit.from_string(html, f'{query_id}.pdf', configuration=config, options=options)
        

        s3 = boto3.client('s3', 
                          aws_access_key_id=os.environ.get("AWS_ACCESS_KEY"), 
                          aws_secret_access_key=os.environ.get("AWS_SECRET_KEY"), 
                          region_name=os.environ.get("REGION_NAME"))
        
        send_complete_parcel_report_email(query.address, query.email, f'https://parcelini-reports.s3.amazonaws.com/{query_id}.pdf')
        
        response = s3.upload_file(f'{query_id}.pdf', 'parcelini-reports', f'{query_id}.pdf')
        os.remove(f'{query_id}.pdf')
        print("DONE!!!!")


        




        

        


def scrape():
    with open('deep_links.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            city = row[0]
            link = row[1]
            if link:
                print("!!"* 100)
                print(city)
                try:
                    traverse(link, city)
                except Exception as e:
                    print(e)
                    print(city, ' has error')

def scrape_county():
    with open('deep_links_county.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            county = row[0]
            link = row[1]
            if link:
                print("!!"* 100)
                print(county)
                try:
                    traverse(link, county=county)
                except Exception as e:
                    print(e)
                    print(county, ' has error')






###############################################################################################




def generate_question(word):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "user", "content": f"Write a GRE question with blank/blanks and four options whose answer is the word '{word}'\n"},
        ]
    )
    return response["choices"][0]["message"]["content"]


from models import TonicQuestion, TonicWord, TonicUser, TonicLesson, TonicScore


def populate_db():
    words = TonicWord.query.all()
    for word_instance in words:
        word = word_instance.word
        question_text = generate_question(word)
        print(question_text)
        try:
            question, options = parse_the_question(question_text)
            correct_options = [option for option in options if word.lower() == option.lower()]
            ques = TonicQuestion(word_id=word_instance.id, openai_text=question_text, question_text=question, 
                                 option1=options[0],option2=options[1],option3=options[2],option4=options[3],correct_answer=correct_options[0])
            db.session.add(ques)
        except:
            ques = TonicQuestion(word_id=word_instance.id, openai_text=question_text)
            db.session.add(ques)

        db.session.commit()


def parse_the_question(question_text):
    divisions = question_text.split("\n")
    pattern = r"_{4,}"
    divisions = [s for s in divisions if s != ""]
    if re.search(pattern, divisions[0]):
        question = divisions[0]
        options = divisions[1:5]
    elif re.search(pattern, divisions[1]):
        question = divisions[1]
        options = divisions[2:6]
    options = [' '.join(options.split(' ')[1:]) for options in options]
    return question, options


@app.route('/generate_lesson/<int:lesson_no>')
def generate_lesson(lesson_no):
    low = (lesson_no-1)*30
    high = (lesson_no)*30

    questions = TonicQuestion.query.all()[low:high]
    
    # question_instances = instances_to_json(questions)

    data = []

    for ques in questions:
        try:
            question_instance = {}
            id = ques.id
            question, options = parse_the_question(ques.openai_text)
            answer = ques.word.word
            question_instance['id'] = id
            question_instance['question'] = question
            question_instance['options'] = options

            correct_options = [option for option in options if answer.lower() == option.lower()]

            if len(correct_options) == 1:
                question_instance['correctAnswer'] = correct_options[0]
                data.append(question_instance)
        except:
            pass
    return data



test_lesson_data=None
with open('lesson_test.json') as f:
    # Load the JSON data from the file
    test_lesson_data = json.load(f)

@app.route('/test_lesson_question_ids')
def test_api_get_question_ids():
    return jsonify(test_lesson_data) 


@app.route('/lesson_question_ids/<user_id>')
def get_lessons_with_question_ids_and_user_progress(user_id):
    lessons = TonicLesson.query.all()
    result = []
    for lesson in lessons[0:1]:
        question_ids = []
        progress_status = []
        for word in lesson.words[:5]:
            for question in word.questions:
                question_ids.append(question.id)
                # Get the progress status for the current user and question
                score = TonicScore.query.filter_by(user_id=user_id, question_id=question.id).first()
                if score:
                    progress_status.append(score.answered_correct)
                else:
                    progress_status.append(None)
        result.append({
            'id': lesson.id,
            'title': lesson.title,
            'question_ids': question_ids,
            'progress_status': progress_status
        })
    return result


@app.route('/update_tonic_score', methods=['POST'])
def update_tonic_score():
    user_id = request.form.get('user_id')
    question_id = request.form.get('question_id')
    answered_correct = bool(request.form.get('answered_correct'))
    ts = TonicScore(user_id=user_id, question_id=question_id, answered_correct=answered_correct)
    db.session.add(ts)
    db.session.commit()
    return '', 204



test_data=None
with open('test.json') as f:
    # Load the JSON data from the file
    test_data = json.load(f)

@app.route('/test_question/<int:question_id>')
def test_question(question_id):
    result = next((item for item in test_data if item["id"] == question_id), None)
    return jsonify(result)




@app.route('/create_user_id')
def create_user_id():
    new_uuid = uuid.uuid4()
    tu = TonicUser(id=str(new_uuid))
    db.session.add(tu)
    db.session.commit()

    return jsonify(tu.id)



def update_gre_words():
    with open('gre_words_1.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            word = row[0].lower()
            print(word)
            frequency = int(row[1])
            existing_word = TonicWord.query.filter_by(word=word).first()
            if existing_word:
                existing_word.frequency = frequency
            else:
                new_word = TonicWord(word=word, frequency=frequency)
                db.session.add(new_word)
        db.session.commit()


def create_lessons():
    words = TonicWord.query.filter_by(lesson_id=None).order_by(sqlalchemy.func.random(), TonicWord.frequency.desc()).all()
    num_words = len(words)
    num_lessons = (num_words // 50) + 1
    print(words)
    
    for i in range(num_lessons):
        lesson_title = f'Common Words - {chr(65+i)}'
        lesson = TonicLesson(title=lesson_title)
        db.session.add(lesson)
        db.session.flush()
        
        for word in words[i*50:(i+1)*50]:
            word.lesson_id = lesson.id
            db.session.add(word)
            
    db.session.commit()





    









    










if __name__ == '__main__':
    app.run(debug=True)
