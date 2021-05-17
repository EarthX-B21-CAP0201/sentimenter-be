from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
import json
import os

load_dotenv()

app = Flask(__name__)
client = MongoClient("mongodb+srv://admin:adminpass@cluster0.h6tnr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

@app.route("/")
def index():
    return "Hello World"

if __name__=="__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)