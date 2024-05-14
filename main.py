from functions import Best_Price_Calculator
from openai import OpenAI
from OpenAI_Sec import Openai_API_key,price_calc_asst_id
from assistant import *
import streamlit as st

client = OpenAI(api_key = Openai_API_key)
#assistant = create_or_retrieve_assistant(client)
#thread = create_thread(client)

st.title("Financial Assistant")

if "assistant" not in st.session_state:
    st.session_state["assistant"] = create_or_retrieve_assistant(client)

if "thread" not in st.session_state:
    st.session_state["thread"] = create_thread(client)

thread = st.session_state.thread

if "last_message_id" not in st.session_state:
    st.session_state.last_message_id = "None"

first_message = """
Hi there! Planning to buy a house, car, or anything else but unsure about how much loan to take and what should be your down payment? I can help you with that and even save you some money. But first, I need a few details from you:

→ Cost of the item you want to buy  
→ Interest rate per year for the loan  
→ Loan tenure (how long the bank will give you the loan for)  
→ Your savings for the purchase  
→ Minimum down payment percentage required by the bank  
→ Your monthly repayment capacity (how much you can pay back each month)  
→ what kind of investments do you usually, like bank FDs, bonds, stocks, gold or real estate. And if you're experienced investor, rate your risk level as high, low, or medium risk taker.
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": first_message}]

#print(st.session_state.messages)
#print(st.session_state.last_message_id)


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    run = user_message(client, thread, prompt, st.session_state.assistant)

    while run_status_check(client,run,thread) != 'completed':
        last_message_id = client.beta.threads.messages.list( thread_id = thread.id).data[0].id
        last_message = client.beta.threads.messages.list( thread_id = thread.id).data[0].content[0].text.value
        print(last_message_id,last_message)

        if last_message_id and last_message_id != st.session_state.last_message_id:

            with st.chat_message("assistant"):
                st.markdown(last_message)

            st.session_state.messages.append({"role": "assistant", "content": last_message})
            st.session_state.last_message_id = last_message_id
    else:
        response_id = client.beta.threads.messages.list( thread_id = thread.id).data[0].id
        response = client.beta.threads.messages.list( thread_id = thread.id).data[0].content[0].text.value

        print(response_id,response)

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.last_message_id = response_id






#if run_status_check(client,run,thread) == 'completed':

#    message_list = client.beta.threads.messages.list(thread_id=thread.id)

#    print(client.beta.threads.messages.list( thread_id = thread.id).data[0].content[0].text.value)








