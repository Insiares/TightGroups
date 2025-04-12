import streamlit as st
import requests
from src.config import Config, logger
import pandas as pd
import time
from components.auth import refresh_access_token

st.title("Setup")


if "registering" not in st.session_state.keys():
    st.session_state.registering = False


def get_ammo():
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.get(f"{Config.BACKEND_URL}/ammo/", headers=headers)
    if response.status_code == 403:  # Code corresponding to token expiration
        st.warning("🔄 Access token expired. Attempting refresh...")
        refresh_access_token()
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.get(f"{Config.BACKEND_URL}/ammo/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"❌ Request failed with status code {response.status_code}.")
        return response


def submit_new_setup(gear, name, ammo, position, drill):
    logger.info(f"Creating setup with : {name},{gear}, {ammo}, {position}, {drill}")
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    payload = {
        "user_id": st.session_state.user_id,
        "gear": gear,
        "name": name,
        "ammo": ammo,
        "position": position,
        "drills": drill,
    }
    response = requests.post(
        f"{Config.BACKEND_URL}/setups/", headers=headers, json=payload
    )
    if response.status_code == 403:  # Code corresponding to token expiration
        st.warning("🔄 Access token expired. Attempting refresh...")
        refresh_access_token()
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.post(
            f"{Config.BACKEND_URL}/setups/", headers=headers, json=payload
        )
    if response.status_code == 200:
        logger.info("Setup created!")
    else:
        logger.error("Setup creation error")
    return response


@st.dialog("Add a New Setup")
def new_setup():
    ammo_list = get_ammo()
    gear = st.text_input("Gear")
    name = st.text_input("Name")
    ammo = st.selectbox("Ammo", ammo_list)
    if st.checkbox("Add missing ammo"):
        ammo = st.text_input("Ammo")
    position = st.text_input("Position")
    drill = st.text_input("Drill")
    submitted = st.button("Submit")
    if submitted:
        logger.info(
            f"Subtimited setup with : {name},{gear}, {ammo}, {position}, {drill}"
        )
        response = submit_new_setup(gear, name, ammo, position, drill)
        if (response is not None) & (response.status_code == 200):
            with st.spinner("Creation Setup..."):
                time.sleep(1)
                st.session_state.registering = False
                st.success("Setup created!")
                st.rerun()
        else:
            st.error("Setup creation error")


def update_session_setup():
    if len(edited_df.selection.rows) > 0:
        st.session_state.setup_id = df["id"].iloc[edited_df.selection.rows].values[0]
        st.session_state.setup_name = (
            df["name"].iloc[edited_df.selection.rows].values[0]
        )


try:
    # headers = {"Content-Type": "application/json"}
    # logger.debug(f" token : {st.session_state['token']}")
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    # logger.debug(f"Headers : {headers}")
    response = requests.get(f"{Config.BACKEND_URL}/setups/", headers=headers)
    if response.status_code == 403:  # Code corresponding to token expiration
        st.warning("🔄 Access token expired. Attempting refresh...")
        refresh_access_token()
        st.rerun()
    setups = response.json()
    logger.info(f"Accessed Setup for user {st.session_state.user_id}")
    # logger.debug(f"Setups : {setups}")
    # logger.debug(f"Setups type : {type(setups)}")

    if len(setups) == 0:
        st.write("No setups found, create one !")
    else:
        df = pd.DataFrame(setups)
        # logger.debug(f"df : {df}")
        edited_df = st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "id": None,
                "user_id": None,
                "created_at": None,
                "name": st.column_config.TextColumn("Name"),
                "gear": st.column_config.TextColumn("Gear"),
                "ammo": None,
                "position": st.column_config.TextColumn("Position"),
                "drills": st.column_config.TextColumn("Drills"),
            },
            # disabled=["id", "created_at", "user_id"],
            hide_index=True,
            selection_mode="single-row",
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

    if st.button("Create New Setup"):
        st.session_state.registering = True
        new_setup()

except Exception as e:
    logger.error(f"Error : {e}")
    st.error(f"Error : {e}")
