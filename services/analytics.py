from flask import Blueprint
from app import app, db, token_required
from flask import request
import time
import json
from datetime import date 



analytics_bp = Blueprint('analytics', __name__)

@token_required
@analytics_bp.route("/top-10/generate", methods=['POST'])
def generateTop10():
    try:
        keyword = request.form.get("keyword")
        hashtag = request.form.get("hashtag")
        category = request.form.get("category")
        language = request.form.get("language")
        location = request.form.get("location")
        is_retweeted = request.form.get("is_retweeted")
        is_realtime = request.form.get("is_realtime")
        date_start = request.form.get("date_start")
        date_end = request.form.get("date_end")
        time.sleep(10)
        return app.response_class(
                response=json.dumps({
                    "message": 'success',
                    "data":[
                        {
                            "name":"ardhito",
                            "count":100

                        },
                         {
                            "name":"ardhito2",
                            "count":200

                        },
                         {
                            "name":"ardhito3",
                            "count":300

                        },
                         {
                            "name":"ardhito4",
                            "count":400

                        },
                         {
                            "name":"ardhito5",
                            "count":500

                        },
                        
                    ],
                    "status": 200,
                }),
                status=200,
                mimetype='application/json')




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




@token_required
@analytics_bp.route("/sentiment/generate", methods=['POST'])
def generateSentiment():
    try:
        keyword = request.form.get("keyword")
        time.sleep(10)
        return app.response_class(
                response=json.dumps({
                    "message": 'success',
                    "data":{
                        "name":"ardhito",
                        "sentiment":"positive",
                        "percentage":20
                    },
                    "status": 200,
                }),
                status=200,
                mimetype='application/json')

    
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


@token_required
@analytics_bp.route("/history", methods=['GET'])
def viewHistory():
    try:
        return app.response_class(
                response=json.dumps({
                    "message": 'success',
                    "data":[
                        {
                            "timestamp":str(date.today()),
                            "type":"sentiment",
                            "topic":"ini keyword yang dicari",


                        },
                         {
                           "timestamp":str(date.today()),
                            "type":"top10",
                            "topic":"ini keyword yang dicari",

                        },
                          {
                           "timestamp":str(date.today()),
                            "type":"top10",
                            "topic":"ini keyword yang dicari",

                        },
                         {
                           "timestamp":str(date.today()),
                            "type":"top10",
                            "topic":"ini keyword yang dicari",

                        },
                         {
                            "timestamp":str(date.today()),
                            "type":"sentiment",
                            "topic":"ini keyword yang dicari",


                        },
                        
                    ],
                    "status": 200,
                }),
                status=200,
                mimetype='application/json')

    
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
