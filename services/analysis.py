from flask import Blueprint, current_app, request
from werkzeug.wrappers import response
from datetime import date, datetime, time, timedelta
from app import app, token_required
from dotenv import load_dotenv
import json
import os
import requests

analysis_bp = Blueprint('analysis', __name__)
load_dotenv()

@analysis_bp.route('')
@token_required
def model_predict():
    model_url = os.environ['MODEL_URL']
    # return json.dumps({"adasd": get_tweet()})

    


def decode_sentiment(prediction, include_neutral:bool = False):
    return False

@analysis_bp.route('/tweet')
def get_tweet():
    query_word = request.args.get("query")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    max_results = request.args.get("max_results")
    tweet_fields = request.args.get("tweet_fields")
    language = request.args.get("language")
    is_retweet = request.args.get("is_retweet")
    annotation = request.args.get("annotation")

    params = dict()

    query = ""
    
    if annotation:
        query = query + annotation

    query = query + query_word

    if not end_time:
        now = datetime.utcnow() - timedelta(minutes=10)
        end_time = now.isoformat("T") + "Z"
        params.update({'end_time': end_time})


    if not start_time:
        last_week = datetime.utcnow() - timedelta(days=7)
        start_time = last_week.isoformat("T") + "Z"
        params.update({'start_time': start_time})

    if is_retweet == "NO":
        query = query + "-is: retweet"
    
    if language:
        query = query + "lang:" + language

    if tweet_fields:
        params.update({'tweet_fields': tweet_fields})
    
    if max_results:
        params.update({'max_results': max_results})


    token = 'Bearer ' + os.environ['BEARER_TOKEN']
    headers = {'Authorization': token}

    params.update({'query': query})

    tweet_search_url = os.environ['TWEET_URL']
    re = requests.get(tweet_search_url, headers=headers, params=params)

    return json.loads(re.text)