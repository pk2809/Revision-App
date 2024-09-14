from flask import Flask  
import views
  
app = Flask(__name__) #creating the Flask class object   
app.register_blueprint(views.page) #registering the blueprint with the Flask class object

if __name__ =='__main__':  
    app.run(debug = True, port=20000)
