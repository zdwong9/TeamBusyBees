from transformers import AutoConfig,AutoModelForSequenceClassification,AutoTokenizer,pipeline

class SentimentModel():

    def __init__(self,text):
        
        config = AutoConfig.from_pretrained('../Trained_Model/config.json')
        model = AutoModelForSequenceClassification.from_pretrained("../Trained_Model/pytorch_model.bin",config=config) 
        tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")

        classifier = pipeline("text-classification",model=model,tokenizer=tokenizer)
        label=classifier(text,truncation=True)[0]["label"]

        if label=="positive":
            encoding=1
        elif label=="neutral":
            encoding=0
        else:
            encoding=2

        return encoding


