import smtplib, ssl
import random, os
import json
from dotenv import load_dotenv
from os.path import join, dirname
from jinja2 import Template


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def send_email(receiver_email, json_content, filename):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = os.environ['sender']  
    password = os.environ['password']

    receiver_email = receiver_email.replace('%40', '@')

    SUBJECT = "Quiz: " + filename   
    TEXT = json.dumps(json_content, indent=4)
    
    email_body = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)


    print('sending email:')
    print(email_body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, email_body)