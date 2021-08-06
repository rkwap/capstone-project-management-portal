import os
from flask import Flask, request, render_template, flash, redirect, url_for, session, Blueprint
from tempfile import mkdtemp
from flask_mysqldb import MySQL
from flask_session import Session
from functools import wraps
from flask_mail import Mail, Message
from flask_recaptcha import ReCaptcha
import requests
import json

app = Flask(__name__, instance_path=os.path.join(os.path.abspath(os.curdir), 'instance'), instance_relative_config=True, static_url_path="", static_folder="static")
app.config.from_pyfile('config.cfg')
app.config['SESSION_FILE_DIR'] = mkdtemp()
mysql=MySQL(app)
Session(app)

def execute_db(query,args=()):
    try:
        cur=mysql.connection.cursor()
        cur.execute(query,args)
        mysql.connection.commit()
    except:
        mysql.connection.rollback()
    finally:
        cur.close()

def query_db(query,args=(),one=False):
    cur=mysql.connection.cursor()
    result=cur.execute(query,args)
    if result>0:
        values=cur.fetchall()
        return values
    cur.close()

def mentor_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def student_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("student_user_id") is None:
            return redirect(url_for("teams.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin")==False:
            return redirect(url_for("mentor.mygroups", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

## Configuring Flask-Mail
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
    MAIL_USERNAME = '',
    MAIL_PASSWORD = ''
	)
mail = Mail(app)

def send_mail(title,sender,recipients,message_html):
    msg = Message(title,
        sender=sender,
        recipients=recipients)
    msg.html = message_html
    mail.send(msg)
    return ("Mail Sent")

## custom filters
@app.template_filter()
def title_split(text):
    new = text.split("*93-k+5=H]s]V%")
    return new[0]

@app.template_filter()
def description_split(text):
    new = text.split("*93-k+5=H]s]V%")
    return new[1]

@app.route('/')
def landing():
    return render_template('landing.html')

## reCaptcha
recaptcha = ReCaptcha(app=app)
SITE_KEY= ""
SECRET_KEY = ""
def is_human(captcha_response):
    # Validating recaptcha response from google server
    # Returns True captcha test passed for submitted form else returns False.
    payload = {'response':captcha_response, 'secret':SECRET_KEY}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']

# Importing Blueprints
from app.views.auth import auth
from app.views.mentor import mentor
from app.views.teams import teams
from app.views.admin import admin

# Registering Blueprints

app.register_blueprint(auth)
app.register_blueprint(mentor)
app.register_blueprint(teams)
app.register_blueprint(admin)
