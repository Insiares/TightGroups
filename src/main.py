import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import Config, logger
import requests

login_page = st.Page("./content/0_login.py", title="Login", icon="🔑")
setup_page = st.Page("./content/1_setup.py", title="Setup", icon="🔧")
seance_page = st.Page("./content/2_seance.py", title="Seance", icon="🎯")
upload_page = st.Page("./content/3_upload.py", title="Upload", icon="📸")
analytics_page = st.Page("./content/4_analytics.py", title="Analytics", icon="📊")


def logout():
    if st.session_state["token"] != "":
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        data = {"refresh_token": st.session_state["refresh_token"]}
        logout_response = requests.post(
            f"{Config.BACKEND_URL}/logout", headers=headers, data=data
        )
        if logout_response.status_code == 200:
            st.success("✅ Logout successful!")

            st.session_state["token"] = None
            st.session_state["refresh_token"] = None
            st.switch_page(login_page)

        else:
            st.error("❌ Logout failed.")
            st.error(f"{logout_response.json()['detail']}")


if "token" not in st.session_state.keys():
    st.session_state.token = None
    logger.info("Token initiated")
if "refresh_token" not in st.session_state:
    st.session_state["refresh_token"] = ""
if "user_id" not in st.session_state.keys():
    st.session_state.user_id = None

if "setup_id" not in st.session_state.keys():
    st.session_state.setup_id = None

if "seance_id" not in st.session_state.keys():
    st.session_state.seance_id = None

if "seance_date" not in st.session_state.keys():
    st.session_state.seance_date = None

if "setup_name" not in st.session_state.keys():
    st.session_state.setup_name = None

if st.session_state.token is None:
    pg = st.navigation(pages=[login_page])

else:
    pg = st.navigation(pages=[setup_page, seance_page, upload_page, analytics_page])
    logger.info("User logged in, redirecting to Setup page")


st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon=":target:",
    layout="wide",
    initial_sidebar_state="auto",
)


st.title(f"{Config.APP_NAME}")
st.sidebar.info(f"Version {Config.VERSION}")
if st.session_state.token is not None:
    if st.sidebar.button("Logout"):
        logout()


pg.run()
