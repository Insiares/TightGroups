import streamlit as st
import requests
from src.config import Config, logger
import pandas as pd
import time
from Meteo.Meteo_API import get_meteo_data
from components.auth import refresh_access_token

st.title("Seances")

if "registering" not in st.session_state.keys():
    st.session_state.registering = False


@st.dialog("Add a New Seance")
def register_new_seance_meteo():
    st.write("To track the weather, please enter your postal code.")
    post_code = st.text_input("Post Code")
    submitted = st.button("Submit")
    if submitted:
        meteo_data = get_meteo_data(post_code)
        logger.info("Subtimited seancei")
        response = submit_new_seance(meteo_data)
        if (response is not None) & (response.status_code == 200):
            with st.spinner("Creating seance..."):
                time.sleep(1)
                st.success("seance created!")
                st.session_state.registering = False
                st.rerun()
        else:
            st.error("seance creation error")


@st.dialog("Add a New Seance")
def new_seance():
    date = st.date_input("Date")
    if st.button("Submit"):
        payload = {
            "temp_C": None,
            "wind_speed": None,
            "wind_gust": None,
            "wind_dir": None,
            "pressure": None,
            "precipitation": None,
            "created_at": str(date),
        }
        response = submit_new_seance(payload)
        if (response is not None) & (response.status_code == 200):
            with st.spinner("Creating seance..."):
                time.sleep(1)
                st.success("seance created!")
                st.session_state.registering = False
                st.rerun()
        else:
            st.error("seance creation error")


def submit_new_seance(meteo_data):
    # add user id to meteo_data json
    meteo_data["user_id"] = st.session_state.user_id
    logger.debug(f"Creating seance with : {meteo_data}")
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.post(
        f"{Config.BACKEND_URL}/seances/", json=meteo_data, headers=headers
    )
    if response.status_code == 403:  # Code corresponding to token expiration
        st.warning("🔄 Access token expired. Attempting refresh...")
        refresh_access_token()
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.post(
            f"{Config.BACKEND_URL}/seances/", json=meteo_data, headers=headers
        )
    if response.status_code == 200:
        logger.info("seance created!")
    else:
        logger.error("seance creation error")
    return response


def update_session_seance():
    # st.session_state.seance_id = df["id"][select]

    # st.write(f"recieved selection : {edited_df.selection}")
    if len(edited_df.selection.rows) > 0:
        st.session_state.seance_id = df["id"].iloc[edited_df.selection.rows].values[0]
        st.session_state.seance_date = (
            df["created_at"].iloc[edited_df.selection.rows].values[0]
        )


try:
    backend_url = Config.BACKEND_URL
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.get(f"{backend_url}/seances/", headers=headers)
    if response.status_code == 403:  # Code corresponding to token expiration
        st.warning("🔄 Access token expired. Attempting refresh...")
        refresh_access_token()
        st.rerun()
    seances = response.json()
    logger.info(f"Accessed seance for user {st.session_state.user_id}")
    if len(seances) == 0:
        st.error("No seances found")
    else:
        df = pd.DataFrame(seances)
        edited_df = st.dataframe(
            df,
            column_config={
                "id": None,
                "user_id": None,
                "created_at": st.column_config.DateColumn(
                    "Date", format="D MMM YYYY, h:mm a", step=60
                ),
                "wind_speed": st.column_config.NumberColumn(
                    "Wind Speed", format="%.2f"
                ),
                "wind_dir": None,
                "precipitation": None,
                "wind_gust": None,
                "pressure": None,
                "temp_C": st.column_config.NumberColumn("Temperature", format="%.2f"),
            },
            selection_mode="single-row",
            on_select="rerun",
            hide_index=True,
            use_container_width=True,
        )

        update_session_seance()
        if st.session_state.seance_id is None:
            st.error("No seance selected")
        else:
            st.success(f"Active seance : {st.session_state.seance_date}")
        # selected_seance = st.selectbox("Select seance", list(seances))
        # st.session_state.seance_id = selected_seance["id"]

        # if st.button("Create New seance"):
        logger.debug(f"Selected seance : {st.session_state.seance_id}")


except Exception as e:
    logger.error(f"Error : {e}")
    st.error(f"Error : {e}")

if st.button("Add a seance"):
    st.session_state.registering = True

if st.session_state.registering:
    seance_map = {
        "new": ":material/partly_cloudy_day:",
        "old": ":material/calendar_month:",
    }
    new_select = st.segmented_control(
        "New Seance",
        options=list(seance_map.keys()),
        format_func=lambda x: seance_map[x],
        selection_mode="single",
    )

    if new_select == "new" and st.session_state.registering:
        register_new_seance_meteo()
    elif new_select == "old" and st.session_state.registering:
        new_seance()
