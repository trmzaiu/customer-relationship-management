import os
from pymongo import MongoClient

connection_string = os.getenv('MONGO_URI', 'mongodb+srv://ismproject:ismproject@ismproject.iao7sef.mongodb.net/test?retryWrites=true&w=majority&appName=ISMProject')
client = MongoClient(connection_string)
db = client.test