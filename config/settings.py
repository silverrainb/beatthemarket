from dotenv import load_dotenv
import os

load_dotenv()

DEBUG = False
LOG_LEVEL = 'DEBUG'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

# For Docker
SERVER_NAME = 'beatthemarket.herokuapp.com'
SECRET_KEY = os.getenv('FLASK_SECRET_KEY')

# NEWS.
API_BASE_URL = os.getenv('API_BASE_URL', 'https://sandbox.iexapis.com/')
MY_API_KEY = os.getenv('MY_API_KEY', 'myapikeys')

# Flask-Mail.
MAIL_DEFAULT_SENDER = 'no-reply@beatthemarket.com'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'eg@example.com')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'placeyouremailpw')

# Celery.
CELERY_BROKER_URL = os.environ.get('REDIS_URL'
                                   , 'redis://:devpassword@redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL'
                                       , 'redis://:devpassword@redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_REDIS_MAX_CONNECTIONS = 5

# SQLAlchemy.
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
                                         'postgresql:///beatthemarket')
SQLALCHEMY_TRACK_MODIFICATIONS = False


# For Docker
# SERVER_NAME = 'localhost:8000'
# SQLALCHEMY_DATABASE_URI = 'postgresql://beatthemarket:devpassword@postgres:5432/beatthemarket'
# SQLALCHEMY_ECHO = True

# User.
# SEED_ADMIN_EMAIL = 'dev@local.host'
# SEED_ADMIN_PASSWORD = 'devpassword'
# from datetime import timedelta
# REMEMBER_COOKIE_DURATION = timedelta(days=90)
