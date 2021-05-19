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
                    "message": 'token is missing'
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
                    "message": 'token is invalid'
                }),
                status=401,
                mimetype='application/json')
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)
    return decorated


@app.route("/")
def index():
    return "Hello World"


@app.route(BASE_URL+"/authentication/signout", methods=['POST'])
@token_required
def signout(current_user):
    try:
        query = {"email": current_user}
        update_query = {"$set": {"token": ""}}
        user_col.update_one(query, update_query)
        response = app.response_class(
            response=json.dumps({
                "message": 'success'
            }),
            status=200,
            mimetype='application/json'
        )
        return response
    except Exception as e:
        print(e)
        response = app.response_class(
            response=json.dumps({
                "message": 'something wrong'
            }),
            status=422,
            mimetype='application/json'
        )
        return response


@app.route(BASE_URL+"/authentication/signup", methods=['POST'])
def signup():
    try:
        email = request.form.get("email")
        password = request.form.get("password")
        salt = bcrypt.gensalt()
        if(is_email_available(email)):
            hashed_password = bcrypt.hashpw(password.encode('utf8'), salt)
            user = {"email": email,
                    "password": hashed_password, "token": ""}
            user_data = user_col.insert_one(user)
            response = app.response_class(
                response=json.dumps({
                    "message": 'success'
                }),
                status=200,
                mimetype='application/json'
            )
            return response

        else:
            response = app.response_class(
                response=json.dumps({
                    "message": 'already exist'
                }),
                status=403,
                mimetype='application/json'
            )
            return response
    except Exception as e:
        print(e)
        response = app.response_class(
            response=json.dumps({
                "message": 'something wrong'
            }),
            status=422,
            mimetype='application/json'
        )
        return response


@app.route(BASE_URL+"/authentication/signin", methods=['POST'])
def signin():
    try:
        email = request.form.get("email")
        password = request.form.get("password")
        query = {"email": email}
        mydoc = list(user_col.find(query))
        if(len(mydoc) > 0):
            password_user = mydoc[0]['password']
            hashed_password = bcrypt.checkpw(
                password.encode('utf-8'), password_user)

            if(hashed_password):
                if(mydoc[0]['token'] == ""):
                    token = jwt.encode({
                        'email': email
                    }, app.config['SECRET_KEY'])
                    update_query = {"$set": {"token": token}}

                    user_col.update_one(query, update_query)
                    response = app.response_class(
                        response=json.dumps({
                            "message": 'success',
                            "user": {
                                "id": str(mydoc[0]['_id']),
                                "email": email,
                                "token": token.decode('utf-8')
                            }
                        }),
                        status=200,
                        mimetype='application/json'
                    )
                    return response
                else:
                    response = app.response_class(
                        response=json.dumps({
                            "message": 'already login',
                        }),
                        status=403,
                        mimetype='application/json'
                    )
                    return response

            else:
                response = app.response_class(
                    response=json.dumps({
                        "message": 'wrong password',
                    }),
                    status=403,
                    mimetype='application/json'
                )
                return response

        else:
            response = app.response_class(
                response=json.dumps({
                    "message": 'email does not exist'
                }),
                status=403,
                mimetype='application/json'
            )
            return response
    except Exception as e:
        print(e)
        response = app.response_class(
            response=json.dumps({
                "message": 'something wrong'
            }),
            status=422,
            mimetype='application/json'
        )
        return response


@app.route(BASE_URL+"/dummy")
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


def is_email_available(email):
    query = {"email": email}
    mydoc = list(user_col.find(query))
    if(len(mydoc) > 0):
        return False
    else:
        return True

# decorator for verifying the JWT


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)
