import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Explicit database path
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'libraries.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Ensure the instance folder exists
    @staticmethod
    def init_app(app):
        os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)