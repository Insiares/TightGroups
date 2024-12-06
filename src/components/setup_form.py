import streamlit as st 
import requests

def setup_form():
    st.write("Setup form")
    with st.form("New Setup"):
        gear = st.text_input("Gear")
        ammo = st.text_input("Ammo")
        position = st.text_input("Position")
        drill = st.text_input("Drill")

        submitted = st.form_submit_button("Submit")
        if submitted:
            payload = {
                "gear"
            }
