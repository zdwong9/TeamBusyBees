from dotenv import load_dotenv
import os
import openai
import streamlit as st
from streamlit_chat import message
from time import sleep
from threading import Thread
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime,timedelta
from model.SummarisationModel import SummarisationModel

# from crawl.crawler import run_crawler

# Setting page title and header
st.set_page_config(page_title="BusyBees", page_icon=":bee:")

# Set API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
uri=os.getenv("DB_STRING")



MODEL = "gpt-3.5-turbo"

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Hi there! Ask me a question."]
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a financial market expert."} 
    ]

if "db_client" not in st.session_state:
    client = MongoClient(uri, server_api=ServerApi('1'))
    mydb = client["news"]
    mycol = mydb["reuters"]
    st.session_state['db_client']=mycol

# if 'started_thread' not in st.session_state:
#     st.session_state['started_thread'] = True
#     def start_thread():
#         while True:
#             run_crawler()
#             sleep(5)
#     Thread(target=start_thread).start()

# generate a response
def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model=MODEL,
        messages=st.session_state['messages']
    )
    response = completion.choices[0].message.content

    st.session_state['messages'].append({"role": "assistant", "content": response})

    return response

def retrieve_docs():

    current_time=datetime.now() + timedelta(-1)
    current_time_str=current_time.strftime("%Y%m%d-%H%M")
    docs=st.session_state["db_client"].find({'datetime': { "$gte": current_time_str}})
    return list(docs)

# @st.cache_data(persist=True)
def retrieve_summary(_docs):
    summary=""
    for doc in _docs:
        summary+= " "+ doc["summary"]
    # return SummarisationModel(summary).get_summary()
    return "Sweden hopes Turkey will ratify the membership when the Turkish parliament reconvenes in October. Initial claims for state unemployment benefits fell 13,000 to 216,000 last week. Deputy leader of Sudan's paramilitary Rapid Support Forces (RSF) says U.S. sanctions are unfair. Proposed changes to a Chinese public security law could criminalise comments, clothing or symbols."

def get_labels(docs):
    return

def main():

    docs=retrieve_docs()
    summary=retrieve_summary(docs)
    st.write(summary)

    

    with st.sidebar:
        st.image(image="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Citi.svg/2560px-Citi.svg.png", width=70)
        response_container = st.container()
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_area("Type your question below:", key='input', height=50)
            submit_button = st.form_submit_button(label='Send')
        if submit_button and user_input:
            output = generate_response(user_input)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)
        
    clear_button = st.sidebar.button("Clear Conversation", key="clear")

    #reset everything
    if clear_button:
        st.session_state['generated'] = ["Hi there! Ask me a question."]
        st.session_state['past'] = []
        st.session_state['messages'] = [
            {"role": "system", "content": "You are a financial market expert."} 
        ]

    #show conversation
    if st.session_state['generated']:
        message(st.session_state["generated"][0], key=str(0), logo=f'https://cdn-icons-png.flaticon.com/512/4712/4712009.png')
        for i in range(len(st.session_state['past'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', logo=f'https://cdn-icons-png.flaticon.com/512/2922/2922719.png')
            message(st.session_state["generated"][i+1], key=str(i+1), logo=f'https://cdn-icons-png.flaticon.com/512/4712/4712009.png')




if __name__=="__main__":
    main()
