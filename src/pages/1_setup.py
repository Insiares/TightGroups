import streamlit as st 
import requests
from src.config import Config, logger

st.title("Setup")

try :
    backend_url = Config.BACKEND_URL
    headers = {"Content-Type": "application/json"}
    response = requests.get(f"{backend_url}/setups/{st.session_state.user_id}/", headers=headers)
    setups = response.json()
    logger.info(f"Accessed Setup for user {st.session_state.user_id}")
    for setup in setups: 
        st.write(setup)

except Exception as e:
    logger.error(f"Error : {e}")
    st.error(f"Error : {e}"
             )
