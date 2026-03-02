import streamlit as st 
import time

if "is_admin" not in st.session_state:
    #데이터를 저장하고 싶을때 
    st.session_state["is_admin"] = False

st.write("Hello")

name = st.text_input("What is your name?")

if name:
    st.write(f"Hello {name}")
    st.session_state["is_admin"] = True

print(st.session_state["is_admin"])