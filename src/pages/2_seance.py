from os import walk
import streamlit as st 
import requests
from src.config import Config, logger
import pandas as pd 
from Meteo.Meteo_API import get_meteo_data
st.title("seance")

def submit_new_seance(meteo_data):
    #add user id to meteo_data json
    meteo_data["user_id"] = st.session_state.user_id
    logger.debug(f"Creating seance with : {meteo_data}")
    response = requests.post(f"{Config.BACKEND_URL}/seances/", json=meteo_data)
    if response.status_code == 200: 
        logger.info("seance created!")
    else : 
        logger.error("seance creation error")
    return response

try :
    backend_url = Config.BACKEND_URL
    headers = {"Content-Type": "application/json"}
    response = requests.get(f"{backend_url}/seances/{st.session_state.user_id}/", headers=headers)
    seances = response.json()
    logger.info(f"Accessed seance for user {st.session_state.user_id}")
    df = pd.DataFrame(seances)
    edited_df = st.dataframe(df, use_container_width=True)

    selected_seance = st.selectbox("Select seance", list(seances))
    st.session_state.seance_id = selected_seance["id"]

   # if st.button("Create New seance"):
    logger.debug(f"Selected seance : {st.session_state.seance_id}")
    with st.form("new_seance", clear_on_submit=True):
        post_code = st.text_input("Post Code")
        submitted = st.form_submit_button("Submit")
        if submitted:
            meteo_data = get_meteo_data(post_code)
            logger.info(f"Subtimited seancei")
            response = submit_new_seance(meteo_data)
            if (response is not None) & (response.status_code == 200):
                st.success("seance created!")
                st.rerun()
            else : 
                st.error("seance creation error")
        
except Exception as e:
    logger.error(f"Error : {e}")
    st.error(f"Error : {e}" )
