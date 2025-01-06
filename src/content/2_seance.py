from os import walk
import streamlit as st 
import requests
from src.config import Config, logger
import pandas as pd
import time
from Meteo.Meteo_API import get_meteo_data
st.title("Seances")

if "registering" not in st.session_state.keys() : 
    st.session_state.registering = False

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

def update_session_seance():
    # st.session_state.seance_id = df["id"][select]
    
    # st.write(f"recieved selection : {edited_df.selection}")
    if len(edited_df.selection.rows) > 0:
        st.session_state.seance_id = df["id"].iloc[edited_df.selection.rows].values[0]
        st.session_state.seance_date = df["created_at"].iloc[edited_df.selection.rows].values[0]


try :
    backend_url = Config.BACKEND_URL
    headers = {"Content-Type": "application/json"}
    response = requests.get(f"{backend_url}/seances/{st.session_state.user_id}/", headers=headers)
    seances = response.json()
    logger.info(f"Accessed seance for user {st.session_state.user_id}")
    if len(seances) == 0:
        st.error("No seances found")
    else :
        df = pd.DataFrame(seances)
        edited_df = st.dataframe(df,
                                 column_config={
                                 "id": None,
                                 "user_id": None,
                                 "created_at": st.column_config.DateColumn("Date", format="D MMM YYYY, h:mm a", step = 60),
                                 "wind_speed": st.column_config.NumberColumn("Wind Speed", format="%.2f"),
                                 "wind_dir" : None,
                                 "precipitation" : None,
                                 "wind_gust" : None,
                                 "pressure" : None,
                                 "temp_C": st.column_config.NumberColumn("Temperature", format="%.2f")
                                 },
                                 selection_mode = "single-row",
                                 on_select = "rerun",
                                 
                                 hide_index = True,

                                 use_container_width=True)

        update_session_seance()
        if st.session_state.seance_id is None:
            st.error("No seance selected")
        else:
            st.success(f"Active seance : {st.session_state.seance_date}")
        # selected_seance = st.selectbox("Select seance", list(seances))
        # st.session_state.seance_id = selected_seance["id"]

       # if st.button("Create New seance"):
        logger.debug(f"Selected seance : {st.session_state.seance_id}")
    if st.button("Create New seance") or st.session_state.registering:
        st.session_state.registering = True
        with st.form("new_seance", clear_on_submit=True):
            post_code = st.text_input("Post Code")
            submitted = st.form_submit_button("Submit")
            if submitted:
                meteo_data = get_meteo_data(post_code)
                logger.info(f"Subtimited seancei")
                response = submit_new_seance(meteo_data)
                if (response is not None) & (response.status_code == 200):
                    with st.spinner("Creating seance..."):
                        time.sleep(2)
                        st.success("seance created!")
                        st.session_state.registering = False
                        st.rerun()
                else : 
                    st.error("seance creation error")
            
except Exception as e:
    logger.error(f"Error : {e}")
    st.error(f"Error : {e}" )
