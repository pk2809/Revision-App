from flask import Flask  
from mysql.connector import connect
from init_db import init
import json
import views
import secrets
  
app = Flask(__name__) #creating the Flask class object   

try:
    with open('config.json', 'r') as file:
        config_data = json.load(file)
        host= config_data["database"]["host"]
        user= config_data["database"]["user"]
        password= config_data["database"]["password"]
except:
    host, user, password = None, None, None

mydb = connect(
    host=host,
    user=user,
    password=password,
)
init(mydb)

blueprint = views.constructBlueprint(mydb)
app.register_blueprint(blueprint) #registering the blueprint with the Flask class object
app.secret_key = secrets.token_urlsafe(16)

if __name__ =='__main__':  
    app.run(debug = True, port=20000)