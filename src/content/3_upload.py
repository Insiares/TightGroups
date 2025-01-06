import streamlit as st 
import requests
from src.config import Config, logger
import base64
from io import BytesIO

st.header("Upload Image")

st.write(f"Add a new image to your active seance ({st.session_state.seance_date}) with selected setup : {st.session_state.setup_name}")
# option = st.radio("Take a picture or upload one ?", ("Take a picture", "Upload an image"))
option = st.toggle("Upload a local image instead of taking one", False)
if not option:
    uploaded_file = st.camera_input("Take a picture...")
else :
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
        
        st.write(f"Predicted group size : {response.json()}")
        
        #TODO : func to display img
        img_response = requests.get(f"{Config.BACKEND_URL}/images/{image_id}/")
        logger.debug(f"img response : {img_response.json()}")
        img_treated_filepath = img_response.json()
        #display image :
        st.image(img_treated_filepath)



    else : 
        st.error("Upload failed!")
        logger.error("Upload failed!"
                     )
        logger.error(f"response : {response.json()}")
