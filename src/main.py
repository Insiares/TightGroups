import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config import Config, logger
login_page = st.Page("pages/0_login.py", title = "Login", icon="🔑")
setup_page = st.Page("pages/1_setup.py", title = "Setup", icon="🔧")
seance_page = st.Page("pages/2_seance.py", title = "Seance", icon="🎯")
upload_page = st.Page("pages/3_upload.py", title = "Upload", icon="📸")
analytics_page = st.Page("pages/4_analytics.py", title = "Analytics", icon="📊")


if "token" not in st.session_state.keys():
    st.session_state.token = None
    logger.info("Token initiated")


if st.session_state.token is None:
    pg = st.navigation(pages=[login_page]
                    )
else : 
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
pg.run()

