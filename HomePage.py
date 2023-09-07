from dotenv import load_dotenv
import os
import openai
import streamlit as st
from streamlit_chat import message

# Setting page title and header
st.set_page_config(page_title="BusyBees", page_icon=":bee:")

# Set API key
load_dotenv()
openai.api_key = os.getenv("KEY")

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Hi there! Ask me a question."]
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a financial market expert."} #maybe can change to a better prompt
    ]

model = "gpt-3.5-turbo"

# generate a response
def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model=model,
        messages=st.session_state['messages']
    )
    response = completion.choices[0].message.content

    st.session_state['messages'].append({"role": "assistant", "content": response})

    print(st.session_state['messages'])
    return response

#sidebar
with st.sidebar:
    st.image(image="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Citi.svg/2560px-Citi.svg.png", width=70)
    # st.sidebar.title("title")
    response_container = st.container()
    with st.form(key='my_form', clear_on_submit=True):
        # user_input = st.text_area("Ask me a question:", key='input', height=50)
        user_input = st.text_area("", key='input', height=60)
        submit_button = st.form_submit_button(label='Send')
    if submit_button and user_input:
        output = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
    
clear_button = st.sidebar.button("Clear Conversation", key="clear")

#clear conversation
if clear_button:
    clear_button = False
    st.session_state['generated'] = ["Hi there! Ask me a question."]
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a financial market expert."} #maybe can change to a better prompt
    ]

#show conversation
if st.session_state['generated']:
    with response_container:
        message(st.session_state["generated"][0], key=str(0), logo=f'https://cdn-icons-png.flaticon.com/512/4712/4712009.png')
        for i in range(len(st.session_state['past'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', logo=f'https://cdn-icons-png.flaticon.com/512/2922/2922719.png')
            message(st.session_state["generated"][i+1], key=str(i+1), logo=f'https://cdn-icons-png.flaticon.com/512/4712/4712009.png')


