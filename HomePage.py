from dotenv import load_dotenv
import os
import openai
import streamlit as st
from streamlit_chat import message

load_dotenv()
# Setting page title and header
st.set_page_config(page_title="BusyBees", page_icon=":bee:")

# Set API key
openai.api_key = os.getenv("KEY")

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."} #maybe can change to a better prompt
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
    # response = "this is a test response"
    st.session_state['messages'].append({"role": "assistant", "content": response})

    print(st.session_state['messages'])
    return response



with st.sidebar:
    st.image(image="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Citi.svg/2560px-Citi.svg.png", width=80)
    # st.sidebar.title("title")
    response_container = st.container()
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("Ask me a question:", key='input', height=50)
        submit_button = st.form_submit_button(label='Send')
    if submit_button and user_input:
        output = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
    
clear_button = st.sidebar.button("Clear Conversation", key="clear")

#reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."} #maybe can change to a better prompt
    ]

#show conversation
if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))


