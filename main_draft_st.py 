
import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
from loguru import logger


logger.add("main_logs.log")

backend_url = "http://0.0.0.0:8000"

def login(username : str, password : str):
    payload = {"username": username, "password": password}
    headers = {"Content-Type" : "application/x-www-form-urlencoded"}
    response = requests.post(f"{backend_url}/token", data=payload, headers = headers)
    if response.status_code == 200:
        # Register user id in session
        logger.debug(f"response : {response.json()}")
        st.session_state.user_id = response.json()["user_id"]
        return response.json()["access_token"]
    else : 
        st.error("Login failed!")
        return None

# TODO : send to components lib
def convert_base64_to_bytesIO(image_base64):
    image_bytes = base64.b64decode(image_base64)
    image_buffer = io.BytesIO()
    image = Image.open(image_bytes)
    image.save(image_buffer, format='JPEG'
               )
    image_buffer.seek(0)
    return image_buffer

def image_base64_to_buffer(image_base64):
    image_buffer = convert_base64_to_bytesIO(image_base64)
    image = Image.open(image_buffer)

    if image.mode == 'RGBA':
        image = image.convert('RGB')

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    return img_byte_arr

if st.button("session"):
    for k,v in st.session_state.items():
        st.write(f"{k}: {v}")
    
if "token" not in st.session_state.keys():
    st.session_state.token = None
    logger.info("Token initiated")

# login form if not already logged in 
if st.session_state.token is None:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        token = login(username, password)
        if token is not None:
            st.session_state.token = token
            logger.info(f"Token assigned for {username}")
            st.success("Login successful!")
            st.rerun()
            
    st.header("Create User")
    username = st.text_input("New_Username")
    email = st.text_input("Email")
    password = st.text_input("New_Password", type="password")
    if st.button("Create User"): 
        payload = {"username": username, "email": email, "password": password}
        headers = {"Content-Type": "application/json"}

        response = requests.post(f"{backend_url}/users/", json=payload, headers = headers)
        st.write(response.json())


else:

    st.title("Test Front-End for Sports Shooter App")
    headers = {"Content-Type": "application/json"}
   # Create Setup
    st.header("Create Setup")
    user_id_setup = st.session_state.user_id

    # get all gear existing for that user and provide it in a dropdown, or allow to create a new one
    gear = st.text_input("Gear")
    if st.button("Get Gear"):
        response = requests.get(f"{backend_url}/gears/{user_id_setup}/")
        st.write(response.json())   
    
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
        img = uploaded_file.getvalue(
        )
        #logger.info(f"Img get value : {type(img)}")
        img_b64 = base64.b64encode(img).decode("utf-8")
        files = { "file" : (uploaded_file.name, BytesIO(img), "image/jpeg")}
        payload = {"user_id": user_id_image, "setup_id": setup_id}


        response = requests.post(f"{backend_url}/upload/?user_id={user_id_image}&setup_id={setup_id}", files=files)
        #response = requests.post(f"{backend_url}/upload/", json=payload, files = files)
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
