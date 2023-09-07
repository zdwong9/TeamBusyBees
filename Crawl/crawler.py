from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from dotenv import load_dotenv
import os

import sys
 
# adding Folder_2 to the system path
sys.path.append('../')

from model.SummarisationModel import SummarisationModel
from model.SentimentModel import SentimentModel

load_dotenv()

uri=os.getenv("DB_STRING")


options = Options()
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

options.set_capability("pageLoadStrategy", "eager")
options.add_argument("--test-type")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
agent="Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36"
options.add_argument(f'user-agent={agent}')

service = Service(executable_path="./chromedriver")
browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
base="https://www.reuters.com/news/archive/finance"


client = MongoClient(uri, server_api=ServerApi('1'))
mydb = client["news"]
mycol = mydb["reuters"]

def main(start,end):
    href_ls=[]

    for i in range(start,end+1):
        browser.get(base+f"?view=page&page={i}&pageSize=10")
        elements=browser.find_elements(By.XPATH, "//article[contains(@class, 'story')]")

        for item in elements:
            # title=item.find_element(By.CLASS_NAME,"story-content").find_element(By.XPATH,"//h3").text
            soup=BeautifulSoup(item.find_element(By.CLASS_NAME,"story-content").get_attribute("innerHTML"), 'lxml').a
            href=soup.get("href")
            print(href,i)
            href_ls.append(("",href))

    res=[]
    for _,href in href_ls:
        browser.get(base+href)
        soup=BeautifulSoup(browser.page_source, 'lxml')

        if len(list(mycol.find({'title': { "$eq": "test"}}))) > 0:
            break

        try:
            title=soup.find_all("h1")[0].text
            print(title)
            content=soup.find_all("h1")[0].find_previous().text.split("/")
            p=soup.find_all("p")
        except:
            continue

        date=content[0].strip()
        time=content[1].strip()
        dt= date+" "+time
        dt=datetime.strptime(dt,"%B %d, %Y %I:%M %p").strftime("%Y%m%d-%H%M")

        body=""
        
        for item in p[1:]:
            if "Reporting by" in item.text:
                break
            body+= " " + item.text

        curr={}
        curr["title"]=title
        curr["body"]=body
        curr["datetime"]=dt
        curr["label"]=SentimentModel(body).get_label()
        curr["summary"]=SummarisationModel(body).get_summary()
        res.append(curr)


    mycol.insert_many(res)

def run_crawler():
    start=2
    end=50

    main(start,end)

if __name__=="__main__":
    main(2,10)