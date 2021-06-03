from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
from flask import request
import bcrypt
import json
import os
import jwt
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
client = MongoClient(
    "mongodb+srv://admin:adminpass@cluster0.h6tnr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

db = client['myFirstDatabase']
user_col = db['users']
history_col = db['history']

BASE_URL = "/api/v1"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return app.response_class(
                response=json.dumps({
                    "message": 'token is missing',
                    "status": 401,
                }),
                status=401,
                mimetype='application/json'
            )

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = data['email']

        except:
            return app.response_class(
                response=json.dumps({
                    "message": 'token is invalid',
                    "status": 401,
                }),
                status=401,
                mimetype='application/json')
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)
    return decorated



from services.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix=BASE_URL+'/authentication')

from services.analytics import analytics_bp
app.register_blueprint(analytics_bp, url_prefix=BASE_URL+'/analytics')

from services.analysis import analysis_bp
app.register_blueprint(analysis_bp, url_prefix=BASE_URL+'/analysis')

@app.route("/")
def index():
    return "Hello World"


@app.route(BASE_URL+"/user/dummy")
def seed_user():
    query = {"email": "dummy@gmail.com"}
    mydoc = list(user_col.find(query))
    if(len(mydoc) > 0):
        return "already created"

    else:
        dummyUser = {"email": "dummy@gmail.com",
                     "password": "dummypassword", "token": ""}
        user = user_col.insert_one(dummyUser)
        return "Inserted with id:" + str(user.inserted_id)


@app.route(BASE_URL+"/user/list")
def see_all_user():

    mydoc = list(user_col.find({}))
    newList = []
    for i in mydoc:

        data = {
            "email": i['email'],
            "password": i['password'],
            "token": i['token'],
            "_id": str(i["_id"])
        }
        newList.append(data)

    return str(newList)


@app.route(BASE_URL+"/user/delete")
def delete_all_user():
    user_col.remove({})
    return "Deleted all user"


# decorator for verifying the JWT

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
