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

config = pdfkit.configuration(wkhtmltopdf='bin/wkhtmltopdf')
from app import parcel_report_template

options = {
    'page-size': 'A4',
    'encoding': "UTF-8",
    'zoom': '0.8',
    'page-width': '*'
}


query_id = '92bcc028-e963-470c-8fae-be3625e1b8a3'
query_id = '4fb7b846-89c1-47a8-bc6c-8dab76795aaf'
html = parcel_report_template(query_id)




if sys.platform == "darwin":
    pdfkit.from_string(html, f'{query_id}.pdf')
else:
    pdfkit.from_string(html, f'{query_id}.pdf', configuration=config, options=options)

s3 = boto3.client('s3', 
                    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY"), 
                    aws_secret_access_key=os.environ.get("AWS_SECRET_KEY"), 
                    region_name=os.environ.get("REGION_NAME"))
response = s3.upload_file(f'{query_id}.pdf', 'parcelini-reports', f'{query_id}.pdf')
os.remove(f'{query_id}.pdf')

