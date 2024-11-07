
import streamlit as st
import requests

backend_url = "http://0.0.0.0:8000"

def login(username : str, password : str):
    payload = {"username": username, "password": password}
    headers = {"Content-Type" : "application/x-www-form-urlencoded"}
    response = requests.post(f"{backend_url}/token", data=payload, headers = headers)
    if response.status_code == 200:
        return response.json()["access_token"]
    else : 
        st.error("Login failed!")
        return None

# session state for auth token
if "token" not in st.session_state:
    st.session_state.token = None

# login form if not already logged in 
if st.session_state.token is None:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        token = login(username, password)
        if token is not None:
            st.session_state.token = token
            st.success("Login successful!")
            st.experimental_rerun()
            
    st.header("Create User")
    username = st.text_input("New_Username")
    email = st.text_input("Email")
    password = st.text_input("New_Password", type="password")
    if st.button("Create User"): 
        payload = {"username": username, "email": email, "password": password}
        print(payload)
        headers = {"Content-Type": "application/json"}

        response = requests.post(f"{backend_url}/users/", json=payload, headers = headers)
        st.write(response.json())


else: 
    st.write(f"Logged in as {st.session_state.token}")

    st.title("Test Front-End for Sports Shooter App")
    headers = {"Content-Type": "application/json"}
# Create User
   # Create Setup
    st.header("Create Setup")
    user_id_setup = st.number_input("User ID for Setup", step=1)
    gear = st.text_input("Gear")
    ammo = st.text_input("Ammo")
    position = st.text_input("Position")
    drills = st.text_input("Drills")
    if st.button("Create Setup"):
        response = requests.post(f"{backend_url}/setups/", json={"user_id": user_id_setup, "gear": gear, "ammo": ammo, "position": position, "drills": drills})
        st.write(response.json())

# Upload Image
    st.header("Upload Image")
    user_id_image = st.number_input("User ID for Image", step=1)
    setup_id = st.number_input("Setup ID", step=1)
    uploaded_file = st.file_uploader("Choose an image...", type="jpg")
    if st.button("Upload Image") and uploaded_file is not None:
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{backend_url}/upload/?user_id={user_id_image}&setup_id={setup_id}", files=files)
        st.write(response.json())

# List User Images
    st.header("List User Images")
    user_id_images = st.number_input("User ID for Images", step=1, key="user_id_images")
    if st.button("List Images"):
        response = requests.get(f"{backend_url}/users/{user_id_images}/images/")
        st.write(response.json())

# List User Setups
    st.header("List User Setups")
    user_id_setups = st.number_input("User ID for Setups", step=1, key="user_id_setups")
    if st.button("List Setups"):
        response = requests.get(f"{backend_url}/setups/{user_id_setups}/")
        st.write(response.json())
