from os import walk
import streamlit as st 
import requests
from src.config import Config, logger
import pandas as pd 
import time
st.title("Setup")


if "registering" not in st.session_state.keys() : 
    st.session_state.registering = False

def submit_new_setup(gear,name, ammo, position, drill):
    logger.info(f"Creating setup with : {name},{gear}, {ammo}, {position}, {drill}")
    payload = {"user_id": st.session_state.user_id, "gear": gear, "name":name, "ammo": ammo, "position": position, "drills": drill}
    response = requests.post(f"{Config.BACKEND_URL}/setups/", json=payload)
    if response.status_code == 200: 
        logger.info("Setup created!")
    else : 
        logger.error("Setup creation error")
    return response

def update_session_setup():
    if len(edited_df.selection.rows) > 0:
        st.session_state.setup_id = df["id"].iloc[edited_df.selection.rows].values[0]
        st.session_state.setup_name = df["name"].iloc[edited_df.selection.rows].values[0]

try :
    backend_url = Config.BACKEND_URL
    headers = {"Content-Type": "application/json"}
    response = requests.get(f"{backend_url}/setups/{st.session_state.user_id}/", headers=headers)
    setups = response.json()
    logger.info(f"Accessed Setup for user {st.session_state.user_id}")
    # logger.debug(f"Setups : {setups}")
    # logger.debug(f"Setups type : {type(setups)}")

    if len(setups) == 0:
        st.write("No setups found, create one !")
    else : 
        df = pd.DataFrame(setups)
        # logger.debug(f"df : {df}")
        edited_df = st.dataframe(df, use_container_width=True, column_config={
                                 "id" : None,
                                 "user_id" : None,
                                 "created_at" : None,
                                 "name": st.column_config.TextColumn("Name"),
                                 "gear": st.column_config.TextColumn("Gear"),
                                 "ammo": None,
                                 "position": st.column_config.TextColumn("Position"),
                                 "drills": st.column_config.TextColumn("Drills"),
        }, 
                                   #disabled=["id", "created_at", "user_id"],
                                   hide_index=True,
                                   selection_mode = 'single-row',
                                   on_select="rerun",
                                   # selected_rows = df.index[df['id']==st.sesion_state.setup_id] if st.session_state.setup_id is not None else []
                                   )
        update_session_setup() 
        logger.debug(f"selection : {edited_df.selection.rows}")
        if st.session_state.setup_id is None:
            st.error("No setup selected")
        else:
            st.success(f"Selected setup : {st.session_state.setup_name}")
            logger.debug(f"Selected setup {st.session_state.setup_id}")


    if st.button("Create New Setup") or st.session_state.registering:
        st.session_state.registering = True
        with st.form("new_setup", clear_on_submit=True):
            name = st.text_input("Name")
            gear = st.text_input("Gear")
            ammo = st.text_input("Ammo")
            position = st.text_input("Position")
            drill = st.text_input("Drills")
            submitted = st.form_submit_button("Submit")
            if submitted:
                logger.info(f"Subtimited setup with : {name},{gear}, {ammo}, {position}, {drill}")
                response = submit_new_setup(gear,name, ammo, position, drill)
                if (response is not None) & (response.status_code == 200):
                    with st.spinner("Creation Setup..."):
                        time.sleep(2)
                        st.session_state.registering = False
                        st.success("Setup created!")
                        st.rerun()
                else : 
                    st.error("Setup creation error")
        
except Exception as e:
    logger.error(f"Error : {e}")
    st.error(f"Error : {e}" )

