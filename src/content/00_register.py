import streamlit as st
import requests
from src.config import Config, logger

st.title("Register")

def register(email : str, username : str, password : str):
    payload = {"username": username, "password": password, "email": email}
    headers = {"Content-Type" : "application/x-www-form-urlencoded"}
    response = requests.post(f"{Config.BACKEND_URL}/users", data=payload, headers = headers)
    if response.status_code == 200:
        logger.debug(f"response : {response.json()}")
        # reroute to login pages
        st.success("Registration successful!")
        st.rerun()
    else : 
        st.error("Registration failed!")
        return None

with st.form("register_form"):
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Register")

    if submitted:
        register(email, username, password) 

# link to login pages if already have an account
st.write("Already have an account? [Login](content/0_login.py)")
