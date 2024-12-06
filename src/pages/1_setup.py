from os import walk
import streamlit as st 
import requests
from src.config import Config, logger
import pandas as pd 
st.title("Setup")

def submit_new_setup(gear, ammo, position, drill):
    logger.info(f"Creating setup with : {gear}, {ammo}, {position}, {drill}")
    payload = {"user_id": st.session_state.user_id, "gear": gear, "ammo": ammo, "position": position, "drills": drill}
    response = requests.post(f"{Config.BACKEND_URL}/setups/", json=payload)
    if response.status_code == 200: 
        logger.info("Setup created!")
    else : 
        logger.error("Setup creation error")
    return response

try :
    backend_url = Config.BACKEND_URL
    headers = {"Content-Type": "application/json"}
    response = requests.get(f"{backend_url}/setups/{st.session_state.user_id}/", headers=headers)
    setups = response.json()
    logger.info(f"Accessed Setup for user {st.session_state.user_id}")
    df = pd.DataFrame(setups)
    edited_df = st.data_editor(df, use_container_width=True,num_rows = "dynamic", column_config={
                             "gear": st.column_config.TextColumn("Gear"),
                             "ammo": st.column_config.Column("Ammo"),
                             "position": st.column_config.TextColumn("Position"),
                             "drills": st.column_config.TextColumn("Drills"),
                             "id": st.column_config.Column("ID")
    })

    select_setup = st.selectbox("Select Setup", list(setups)
                           )
    st.session_state.setup_id = select_setup["id"]
    logger.debug(f"Selected setup {st.session_state.setup_id}")
   # if st.button("Create New Setup"):

    with st.form("new_setup", clear_on_submit=True):
        gear = st.text_input("Gear")
        ammo = st.text_input("Ammo")
        position = st.text_input("Position")
        drill = st.text_input("Drills")
        submitted = st.form_submit_button("Submit")
        if submitted:
            logger.info(f"Subtimited setup with : {gear}, {ammo}, {position}, {drill}")
            response = submit_new_setup(gear, ammo, position, drill)
            if (response is not None) & (response.status_code == 200):
                st.success("Setup created!")
                st.rerun()
            else : 
                st.error("Setup creation error")
        
except Exception as e:
    logger.error(f"Error : {e}")
    st.error(f"Error : {e}" )

