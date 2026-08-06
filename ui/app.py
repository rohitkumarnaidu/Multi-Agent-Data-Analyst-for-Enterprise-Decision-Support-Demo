import streamlit as st
import requests
import json
import os

# API URL
API_URL = os.environ.get("API_URL", "http://localhost:8000/chat")

st.set_page_config(page_title="Data Analyst Agents", page_icon="🤖", layout="wide")

st.title("🤖 Multi-Agent Enterprise Data Analyst")
st.markdown("Ask natural language questions about the Olist E-commerce dataset!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask a question (e.g. 'What are the top 3 product categories by revenue?')"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("The agent crew is thinking..."):
            try:
                response = requests.post(API_URL, json={"query": prompt}, timeout=120)
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer provided.")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error {response.status_code}: {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = f"API Request failed: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
