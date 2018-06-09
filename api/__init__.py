import os

from flask import Flask
from flask_pymongo import PyMongo
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache(threshold = 1000, default_timeout = 100)

application = Flask(__name__, static_folder='/app/static', template_folder='/app/template')

application.config['MONGO_DBNAME'] = os.environ['MONGO_DBNAME']
application.config['MONGO_URI'] = os.environ['MONGO_URI']

mongo = PyMongo(application)


class MongoException(Exception):
    pass
