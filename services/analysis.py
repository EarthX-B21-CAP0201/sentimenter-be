from flask import Blueprint, current_app, request
from werkzeug.wrappers import response
from datetime import date, datetime, time, timedelta
from app import app, token_required, db
from dotenv import load_dotenv
from collections import Counter
import json
import os, sys
import requests
import pickle
import numpy as np
from keras.preprocessing.sequence import pad_sequences

analysis_bp = Blueprint('analysis', __name__)
history_col = db['history']
load_dotenv()

@analysis_bp.route('', methods=['POST'])
# @token_required
def model_predict(current_user):

    data = dict()
    keyword = request.form.get('keyword')
    language = "en"
    data.update({
        'keyword':keyword,
        'lang':language,
        'max_results':50
    })
    prediction_url = os.environ['MODEL_URL']+':predict'

    try:
        tweets = get_tweet(data)
    except Exception as e:
        print(e)
        response = app.response_class(
            response=json.dumps({
                "message": 'something wrong'
            }),
            status=400,
            mimetype='application/json'
        )
        return response

    predictions = []

    for tweet in tweets:
        tokenized_tweet = tokenize_tweets(tweet)
        body = dict(
            instances=tokenized_tweet.tolist()
        )
        re = requests.post(url=prediction_url, data=json.dumps(body))
        # predictions
        json_response = json.loads(re.text)
        prediction = json_response['predictions'][0][0]

        decoded_prediction = decode_sentiment(prediction, include_neutral=True)

        predictions.append(decoded_prediction)
    
    sentiment, occurrence = prediction_counter(predictions)
    percent = (occurrence/len(predictions)) * 100
    print(percent)
    
    if re.status_code != 200:
        response = app.response_class(
            response=json.dumps({
                "message": 'something wrong'
            }),
            status=400,
            mimetype='application/json'
        )
        return response

    result_json = {
        "name":data['keyword'],
        "sentiment":sentiment,
        "percentage":percent,
        "total_tweet": len(tweets)
    }

    history = {
        "user":current_user,
        "date_created": str(date.today()),
        "type":"Sentiment Analysis",
        "keyword":keyword,
        "result": result_json
    }
    try:
        history_data = history_col.insert_one(history)
    except Exception as e:
        raise "Failed to insert to database"
    
    response = app.response_class(
        response=json.dumps({
                "message": 'Success',
                "data": result_json,
                "status": 200,
            }),
        status=200,
        mimetype='application/json'
    )

    return response


def decode_sentiment(score, include_neutral:bool = False):
    if include_neutral:        
        label = "NEUTRAL"
        if score <= 0.33:
            label = "NEGATIVE"
        elif score >= 0.66:
            label = "POSITIVE"

        return label
    else:
        return "NEGATIVE" if score < 0.5 else "POSITIVE"

def get_tweet(data):
    query_word = data.get("keyword")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    max_results = data.get("max_results")
    tweet_fields = data.get("tweet_fields")
    language = data.get("language")
    is_retweet = data.get("is_retweet")
    annotation = data.get("annotation")

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
        query = query + " -is: retweet"
    
    if language:
        query = query + " lang:" + language

    if tweet_fields:
        params.update({'tweet_fields': tweet_fields})
    
    if max_results:
        params.update({'max_results': max_results})
    else:
        params.update({'max_results': 100})


    token = 'Bearer ' + os.environ['BEARER_TOKEN']
    headers = {'Authorization': token}

    params.update({'query': query})

    tweet_search_url = os.environ['TWEET_URL']
    print(params)
    re = requests.get(tweet_search_url, headers=headers, params=params)

    tweets = [x['text'] for x in json.loads(re.text)["data"]]

    return tweets

def load_tokenizer():
    files = os.path.join(sys.path[0], 'services/tokenizer.pickle')
    with open(files, 'rb') as handle:
        tokenizer = pickle.load(handle)

    return tokenizer

def tokenize_tweets(tweet):
    tokenizer = load_tokenizer()
    tokenized = pad_sequences(tokenizer.texts_to_sequences([tweet]), maxlen=300)

    return tokenized

def prediction_counter(predictions):
    count = Counter(predictions)
    return count.most_common()[0]