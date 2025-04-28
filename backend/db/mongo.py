from pymongo import MongoClient

client = MongoClient("mongodb+srv://ismproject:<db_password>@ismproject.iao7sef.mongodb.net/?retryWrites=true&w=majority&appName=ISMProject")
db = client.mydatabase