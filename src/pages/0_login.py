import streamlit as st 
import requests
from src.config import Config, logger

st.title("Login")

def login(username : str, password : str):
    payload = {"username": username, "password": password}
    headers = {"Content-Type" : "application/x-www-form-urlencoded"}
    response = requests.post(f"{Config.BACKEND_URL}/token", data=payload, headers = headers)
    if response.status_code == 200:
        # Register user id in session
        logger.debug(f"response : {response.json()}")
        st.session_state.user_id = response.json()["user_id"]
        return response.json()["access_token"]
    else : 
        st.error("Login failed!")
        return None

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

    if submitted:
        token = login(username, password)
        if token is not None:
            st.session_state.token = token
            logger.info(f"Token assigned for {username}")
            st.success("Login successful!")
            st.rerun()
