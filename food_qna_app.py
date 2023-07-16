import streamlit as st 
from streamlit_chat import message
import os

from redis_db import create_redis_client, get_redis_results
from chatbot import LLMAssistant, Message

redis_client = create_redis_client()

system_prompt = '''
As a devoted personal assistant, you possess the ability to expertly address 
any of user inquiries regarding food recipes. User can count on you to provide 
valuable assistance in all matters related to food preparation and cooking.

Think about this step by step: 
- The user will ask a question related to food preparation and cooking. 
- If you are confident this is question related to food preparation and cooking, start saying "Certianly", 
  and answer the user's question using retrieved results from a database; 
  otherwise, say "Sorry, I can only help answer questions related to food preparation and cooking at the moment..."

Example: 

Here's how our interaction will unfold step by step:

User: "I'd like to know how to make banana ice cream."
Assistant: Certainly, ...

User: "I'd like to know how to book a flight."
Assistant: Sorry, I don't know how to book a flight. I can only help answer questions related to food preparation and cooking at the moment...
Feel free to ask any culinary questions, and I'll be more than happy to assist you in your gastronomic endeavors!
'''

st.set_page_config(
    page_title="Food QnA - Demo", 
    page_icon="👩‍🍳"
)

st.title('Food QnA Chatbot 🍱 🥗 🍰 😋')
st.subheader('Help answer questions from your own cookbook~~~')
st.write(
    "Has environment variables for LLM API key been set:",
    os.environ["OPENAI_API_KEY"] == st.secrets["OPENAI_API_KEY"],
)

if 'generated' not in st.session_state: 
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

def query(question):
    response = st.session_state['chat'].ask_llm_assistant(question)
    return response 

prompt = st.text_input(f"What do you want to know? ", key="input")

if st.button('Submit', key='generationSubmit'):
    if 'chat' not in st.session_state:
        st.session_state['chat'] = LLMAssistant()
        messages = []
        system_message = Message('system',system_prompt)
        messages.append(system_message.message())
    else:
        messages = []


    user_message = Message('user',prompt)
    messages.append(user_message.message())

    response = query(messages)

    # Debugging step to print the whole response
    #st.write(response)

    st.session_state.past.append(prompt)
    st.session_state.generated.append(response['content'])

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')