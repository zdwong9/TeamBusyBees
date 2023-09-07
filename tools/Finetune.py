from datasets import load_dataset
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification,Trainer, TrainingArguments
import evaluate
import torch
import numpy

from model.NewsDataset import NewsDataset
from dotenv import load_dotenv
import os
load_dotenv()

uri=os.getenv("DB_STRING")

client = MongoClient(uri, server_api=ServerApi('1'))
mydb = client["news"]
mycol = mydb["reuters"]

data=mycol.find({},{})

dataset=pd.DataFrame(list(data))

def split_dataset(df):
    texts = []
    labels = []
    df=df.loc[:,["body","label"]]
    for idx,row in df.iterrows():
        texts.append(row["body"])
        labels.append(row["label"])
    return texts, labels

train, test = train_test_split(dataset, test_size=0.2)
train_texts, train_labels = split_dataset(train)
test_texts, test_labels = split_dataset(test)
train_texts, val_texts, train_labels, val_labels = train_test_split(train_texts, train_labels, test_size=.2)

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

train_encodings = tokenizer(train_texts, truncation=True, padding=True)
val_encodings = tokenizer(val_texts, truncation=True, padding=True)
test_encodings = tokenizer(test_texts, truncation=True, padding=True)

train_dataset = NewsDataset(train_encodings, train_labels)
val_dataset = NewsDataset(val_encodings, val_labels)
test_dataset = NewsDataset(test_encodings, test_labels)

training_args = TrainingArguments(
    output_dir='./Results',          # output directory
    num_train_epochs=3,              # total number of training epochs
    per_device_train_batch_size=16,  # batch size per device during training
    per_device_eval_batch_size=64,   # batch size for evaluation
    warmup_steps=500,                # number of warmup steps for learning rate scheduler
    weight_decay=0.01,               # strength of weight decay
    logging_dir='./logs',            # directory for storing logs
    logging_steps=10,
)

trainer = Trainer(
    model=model,                         # the instantiated 🤗 Transformers model to be trained
    args=training_args,                  # training arguments, defined above
    train_dataset=train_dataset,         # training dataset
    eval_dataset=val_dataset,             # evaluation dataset
    )

trainer.train()

model.save_pretrained("reuters_news_model")
