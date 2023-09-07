from transformers import pipeline

class SummarisationModel():
    def __init__(self,article) :
        
        classifier = pipeline("summarization",model="facebook/bart-large-cnn",max_length=1024)
        # try:
        self.res=classifier(article,truncation=True)[0]
        # except:
        #     self.res = None
    def get_summary(self):
        if self.res is None:
            return "Cant summarise article"
        return self.res["summary_text"]
    
