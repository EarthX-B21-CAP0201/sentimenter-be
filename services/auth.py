
from flask import Blueprint
from app import app, db, token_required
from flask import request
import bcrypt
import json
import os
import jwt
from functools import wraps


user_col = db['users']
auth_bp = Blueprint('auth', __name__)





@auth_bp.route("/signout", methods=['POST'])
@token_required
def signout(current_user):
    try:
        query = {"email": current_user}
        update_query = {"$set": {"token": ""}}
        user_col.update_one(query, update_query)
        response = app.response_class(
            response=json.dumps({
                "message": 'success',
                "status": 200,
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


@auth_bp.route("/signup", methods=['POST'])
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
                    "message": 'success',
                    "status": 200,
                }),
                status=200,
                mimetype='application/json'
            )
            return response

        else:
            response = app.response_class(
                response=json.dumps({
                    "message": 'already exist',
                    "status": 403,
                }),
                status=403,
                mimetype='application/json'
            )
            return response
    except Exception as e:
        print(e)
        response = app.response_class(
            response=json.dumps({
                "message": 'something wrong',
                "status": 422,
            }),
            status=422,
            mimetype='application/json'
        )
        return response


@auth_bp.route("/signin", methods=['POST'])
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
                            "status": 200,
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
                            "status": 403,
                        }),
                        status=403,
                        mimetype='application/json'
                    )
                    return response

            else:
                response = app.response_class(
                    response=json.dumps({
                        "message": 'wrong password',
                        "status": 403,
                    }),
                    status=403,
                    mimetype='application/json'
                )
                return response

        else:
            response = app.response_class(
                response=json.dumps({
                    "message": 'email does not exist',
                    "status": 403,
                }),
                status=403,
                mimetype='application/json'
            )
            return response
    except Exception as e:
        print(e)
        response = app.response_class(
            response=json.dumps({
                "message": 'something wrong',
                "status": 422,
            }),
            status=422,
            mimetype='application/json'
        )
        return response


def is_email_available(email):
    query = {"email": email}
    mydoc = list(user_col.find(query))
    if(len(mydoc) > 0):
        return False
    else:
        return True
