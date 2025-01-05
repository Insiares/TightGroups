import streamlit as st 
import requests
from src.config import Config, logger
import time
st.title("Login")

if "registering" not in st.session_state.keys() : 
    st.session_state.registering = False


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


def register(email : str, username : str, password : str):
    payload = {"username": username, "password": password, "email": email}
    headers = {"Content-Type" : "application/json"}
    response = requests.post(f"{Config.BACKEND_URL}/users/", json=payload, headers = headers)
    if response.status_code == 200:
        logger.debug(f"response : {response.json()}")
        # reroute to login pages
        st.success("Registration successful!")
        time.sleep(2)
        return 'OK'
    else : 
        st.error("Registration failed!")
        logger.error(f"Error : {response.json()}"
                     )
        time.sleep(5)
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

if st.button("Don't Have an account? Register") or st.session_state.registering:
    st.session_state.registering = True
    with st.form("register_form"):
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Register")

        if submitted:
            result = register(email, username, password)
            if result == 'OK':
                with st.spinner('Redirecting to login page...'):
                    time.sleep(2)
                    st.session_state.registering = False
                    st.rerun()
                
