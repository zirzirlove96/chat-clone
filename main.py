import streamlit as st 
import time

st.write("Hello world!")

st.button("Click me Please!")

st.text_input("Write your API KEY", max_chars=20)

st.feedback("faces")

tab1,tab2,tab3 = st.tabs(["Agent","Chat","Ouput"])

with tab1:
    st.header("Agent")
with tab2:
    st.header("Agent1")
with tab3:
    st.header("Agent2")

with st.chat_message("ai"):
    st.text("Hello!")
    with st.status("Agent is using tool") as status:
        time.sleep(1)
        status.update(label = "Agent is searching the web...")
        time.sleep(2)
        status.update(label = "Agent is reading the web...")
        time.sleep(2)
        status.update(label = "Complet!")

with st.chat_message("human"):
    st.text("Hi")

st.chat_input("Wrtie a message for the assistant.",accept_file=True)
