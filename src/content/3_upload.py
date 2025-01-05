import streamlit as st 
import requests
from src.config import Config, logger
import base64
from io import BytesIO

st.header("Upload Image")
uploaded_file = st.file_uploader("Choose an image...", type="jpg")
if st.button("Upload Image") and uploaded_file is not None:
    img = uploaded_file.getvalue(
    )
    #logger.info(f"Img get value : {type(img)}")
    img_b64 = base64.b64encode(img).decode("utf-8")
    files = { "file" : (uploaded_file.name, BytesIO(img), "image/jpeg")}
    payload =  {"setup_id": st.session_state.setup_id, "seance_id": st.session_state.seance_id}

    response = requests.post(f"{Config.BACKEND_URL}/upload/", data=payload, files=files)
    #response = requests.post(f"{backend_url}/upload/", json=payload, files = files)
    if response.status_code == 200: 
        # retrieve image_id from response and run inference
        image_id = response.json()["id"]
        logger.info(f"image_id : {image_id}")
        payload = {"image_id": image_id, "seance_id": st.session_state.seance_id}
        with st.spinner("Running inference..."):
            response = requests.post(f"{Config.BACKEND_URL}/inference/{st.session_state.seance_id}/{image_id}/")
        st.write(response.json()
                 )
    else : 
        st.error("Upload failed!")
        logger.error("Upload failed!"
                     )
        logger.error(f"response : {response.json()}")
