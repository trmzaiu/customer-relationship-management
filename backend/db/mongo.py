from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://ismproject:ismproject@ismproject.veyygnr.mongodb.net/?retryWrites=true&w=majority&appName=ISMProject"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Select the database
db = client['ismproject']  # Case-sensitive: use 'ismproject' as shown in your URI

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    
    # Print all collection names in the database
    collections = db.list_collection_names()
    print("Collections in the 'ismproject' database:")
    for collection in collections:
        print(f"- {collection}")
    
except Exception as e:
    print("Error:", e)