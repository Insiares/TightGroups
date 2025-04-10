import streamlit as st
from src.config import Config
import requests

BACKEND_URL = Config.BACKEND_URL


def refresh_access_token():
    if st.session_state["refresh_token"] != "":
        refresh_token_url = f"{BACKEND_URL}/refresh"
        headers = {"Authorization": f"Bearer {st.session_state['refresh_token']}"}
        response = requests.post(refresh_token_url, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            st.session_state["token"] = token_data.get("access_token")
            st.session_state["refresh_token"] = token_data.get("refresh_token")
            # st.success("🔄 Token refreshed successfully!")
            # st.write("Access Token:", st.session_state['token'])
            # st.write("Refresh Token:", st.session_state['refresh_token'])
            return st.session_state["token"]
        else:
            st.error("Failed to refresh access token.")
            return response


def make_authenticated_request(
    endpoint: str, payload: dict = None
) -> requests.Response:
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.get(f"{BACKEND_URL}/{endpoint}", headers=headers)
    # logger.debug(f"Response: {response}")
    if response.status_code == 403:  # Code corresponding to token expiration
        st.warning("🔄 Access token expired. Attempting refresh...")
        refresh_access_token()
        # logger.debug(f"New requests with refreshed tokens")
        headers["Authorization"] = f"Bearer {st.session_state['access_token']}"
        new_response = requests.get(f"{BACKEND_URL}/{endpoint}", headers=headers)
        return new_response
    elif response.status_code == 200:
        return response
    else:
        st.error(f"❌ Request failed with status code {response.status_code}.")
        return response
