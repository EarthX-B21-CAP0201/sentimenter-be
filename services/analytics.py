from flask import Blueprint
from app import app, db, token_required
from flask import request
import time
import json
from datetime import date 


history_col = db['history']
analytics_bp = Blueprint('analytics', __name__)

#ENUM FOR CATEGORY
#Brand, Movie, Video Game, Musician, Actor

enum = {
    "Brand":47,
    "Movie":86,
    "Video Game":71,
    "Musician":54,
    "Actor":55
}


@analytics_bp.route("/top-10/generate", methods=['POST'])
@token_required
def generateTop10(current_user):
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

    
      

        # TODO
        # CALL ML SERVICE FUNCTION
        # REMOVE SLEEP
        time.sleep(10)



        #TODO
        #GET DATA RESULT FROM ML SERVICE
        #CHANGE THE ACTUAL RESULT
        
        history = {
            "user":current_user,
            "date_created": str(date.today()),
            "type":"Top 10 Graph",
            "keyword":keyword,
            "hashtag":hashtag,
            "category":category,
            "language":language,
            "location":location,
            "is_retweeted":is_retweeted,
            "is_realtime":is_realtime,
            "date_start":str(date_start),
            "date_end": str(date_end),
            "result": []
        }
      
        history_data = history_col.insert_one(history)
        

        # TODO 
        # CHANGE WITH ACTUAL RESULT WITH SAME STRUCTURE
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





@analytics_bp.route("/sentiment/generate", methods=['POST'])
@token_required
def generateSentiment(current_user):
    try:
        keyword = request.form.get("keyword")
       

        # TODO
        # CALL ML SERVICE FUNCTION
        # REMOVE SLEEP
        time.sleep(10)



        #TODO
        #GET DATA RESULT FROM ML SERVICE
        #CHANGE THE ACTUAL RESULT
        
        history = {
            "user":current_user,
            "date_created": str(date.today()),
            "type":"Sentiment Analysis",
            "keyword":keyword,
            "result": {}
        }
      
        history_data = history_col.insert_one(history)
        

        #TODO
        #CHANGE THE ACTUAL DATA RESULT
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


@analytics_bp.route("/history", methods=['GET'])
@token_required
def viewHistory(current_user):
    try:
        query = {"user" : current_user}
        mylist = list(history_col.find(query))
        result_list = []
        if(len(mylist)>10):
            result_list = mylist[0:10]
        else:
            result_list = mylist
        

        for i in range(0,len(result_list)):
            temp_list = result_list[i]
            temp_list["_id"] = str(temp_list["_id"])
            result_list[i] = temp_list
        
        return app.response_class(
                response=json.dumps({
                    "message": 'success',
                    "data":result_list,
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
