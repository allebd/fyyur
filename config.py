import os
from dotenv import load_dotenv

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
dotenv_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv('DATABASE_URL')

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False
