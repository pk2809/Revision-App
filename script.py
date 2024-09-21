from flask import Flask  
from mongo import get_client
import json
import views
import secrets
  
app = Flask(__name__) #creating the Flask class object   

try:
    with open('config.json', 'r') as file:
        config_data = json.load(file)
        uri = config_data["database"]["uri"]
except:
    uri = ""

mongo_client = get_client(uri)
if mongo_client:
    print("Connected to DB")
else:
    print("Failed to connect to DB")

blueprint = views.constructBlueprint(mongo_client)
app.register_blueprint(blueprint) #registering the blueprint with the Flask class object
app.secret_key = secrets.token_urlsafe(16)

if __name__ =='__main__':  
    app.run(debug = True, port=20000)