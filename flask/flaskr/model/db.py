from pymongo import MongoClient
import os

db = None
client = None

def start():
    # This line creates a database engine that knows how to connect to the URI above.
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret.txt'), 'r') as f:
        DATABASEURI = f.read()
    try:
        global db
        global client
        client = MongoClient(DATABASEURI, w=1)
        db = client['pubmed']
    except:
        print("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()

def get_db():
    # get the connection to the database
    return db

def close(exception):
    try:
        client.close()
    except Exception as e:
        pass
