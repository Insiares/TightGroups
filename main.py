
import streamlit as st
import requests

backend_url = "http://0.0.0.0:8000"

st.title("Test Front-End for Sports Shooter App")
headers = {"Content-Type": "application/json"}
# Create User
st.header("Create User")
username = st.text_input("Username")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
if st.button("Create User"): 
    payload = {"username": username, "email": email, "password": password}
    print(payload)
    response = requests.post(f"{backend_url}/users/", json=payload, headers = headers)
    st.write(response.json())

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
