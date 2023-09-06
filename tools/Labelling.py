# Load model directly
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime,timedelta
from transformers import BertTokenizer, BertForSequenceClassification,pipeline

from dotenv import load_dotenv
import os
load_dotenv()

uri=os.getenv("DB_STRING")

client = MongoClient(uri, server_api=ServerApi('1'))
mydb = client["news"]
mycol = mydb["reuters"]

model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

def load_dataset():
    data=mycol.find({},{"body":1,"datetime":1})
    classifier = pipeline("text-classification",model="ProsusAI/finbert")

    for i in data:

        label=classifier(i["title"],truncation=True)[0]["label"]
        if label=="positive":
            out=1
        elif label=="neutral":
            out=0
        else:
            out=2
        mycol.update_one({"_id":i["_id"]},{"$set":{"label": out}})

load_dataset()