import streamlit as st
import requests
from src.config import Config, logger
import base64
from io import BytesIO
from components.auth import refresh_access_token

if "image_id" not in st.session_state.keys():
    st.session_state.image_id = None


def upload(file, payload):
    try:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.post(
            f"{Config.BACKEND_URL}/upload/", data=payload, files=file, headers=headers
        )
        if response.status_code == 403:  # Code corresponding to token expiration
            st.warning("🔄 Access token expired. Attempting refresh...")
            refresh_access_token()
            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
            response = requests.post(
                f"{Config.BACKEND_URL}/upload/",
                data=payload,
                files=file,
                headers=headers,
            )
        if response.status_code == 200:
            return response
        else:
            st.error("Upload failed!")
            return None

    except Exception as e:
        logger.error(f"Error: {e}")
        return None


def run_inference(payload):
    try:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.post(
            f"{Config.BACKEND_URL}/inference/", headers=headers, data=payload
        )
        if response.status_code == 403:  # Code corresponding to token expiration
            st.warning("🔄 Access token expired. Attempting refresh...")
            refresh_access_token()
            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
            response = requests.post(
                f"{Config.BACKEND_URL}/inference/", headers=headers, data=payload
            )
        if response.status_code == 200:
            st.success("Inference successful!")
            return response
        else:
            st.error("Inference failed!")
            return None

    except Exception as e:
        logger.error(f"Error: {e}")


def handle_failure(image_id):
    try:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        data = {"image_id": image_id}
        response = requests.post(
            f"{Config.BACKEND_URL}/detection_failure/", headers=headers, data=data
        )
        if response.status_code == 403:  # Code corresponding to token expiration
            st.warning("🔄 Access token expired. Attempting refresh...")
            refresh_access_token()
            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
            response = requests.post(
                f"{Config.BACKEND_URL}/detection_failure/", headers=headers, data=data
            )
        if response.status_code == 200:
            st.warning(
                "Thanks for the feedback, your failed prediction run has been removed from your data."
            )
            return response
        else:
            st.error("Image not found!")
            return None

    except Exception as e:
        logger.error(f"Error: {e}")


def get_image(image_id):
    try:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.get(
            f"{Config.BACKEND_URL}/images/{image_id}/", headers=headers
        )
        if response.status_code == 403:  # Code corresponding to token expiration
            st.warning("🔄 Access token expired. Attempting refresh...")
            refresh_access_token()
            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
            response = requests.get(
                f"{Config.BACKEND_URL}/images/{image_id}/", headers=headers
            )
        if response.status_code == 200:
            return response
        else:
            st.error("Image not found!")
            return None

    except Exception as e:
        logger.error(f"Error: {e}")


st.header("Upload Image")

st.write(
    f"Add a new image to your active seance ({st.session_state.seance_date}) with selected setup : {st.session_state.setup_name}"
)
if st.session_state.seance_id is None:
    st.error("You need to select a seance first!")
if st.session_state.setup_id is None:
    st.error("You need to select a setup first!")
# option = st.radio("Take a picture or upload one ?", ("Take a picture", "Upload an image"))
upload_map = {0: ":material/photo_camera:", 1: ":material/upload:"}
option = st.segmented_control(
    "Take a picture or upload one ?",
    options=upload_map.keys(),
    format_func=lambda option: upload_map[option],
    selection_mode="single",
)
# st.write(option)
# st.write(upload_map[option])
# option = st.toggle("Upload a local image instead of taking one", False)
if not option:
    uploaded_file = st.camera_input("Take a picture...")
else:
    uploaded_file = st.file_uploader("Choose an image...", type="jpg")


if st.button("Upload Image") and uploaded_file is not None:
    st.session_state.image_id = None
    img = uploaded_file.getvalue()
    # logger.info(f"Img get value : {type(img)}")
    img_b64 = base64.b64encode(img).decode("utf-8")
    files = {"file": (uploaded_file.name, BytesIO(img), "image/jpeg")}
    payload = {
        "seance_id": str(st.session_state.seance_id),
        "setup_id": str(st.session_state.setup_id),
    }

    response = upload(files, payload)

    if response:
        image_id = response.json()["id"]
        st.session_state.image_id = image_id
        logger.info(f"image_id : {image_id}")
        payload = {
            "image_id": str(image_id),
            "seance_id": str(st.session_state.seance_id),
        }
        with st.spinner("Running inference..."):
            response_inference = run_inference(payload)

        if response_inference:
            st.write(f"Predicted group size : {response_inference.json()}")

            img_response = get_image(image_id)
            img_treated_filepath = img_response.json()
            # display image :
            st.image(img_treated_filepath)
            # st.write("If something went wrong, please let us know! (you can always retake the photo with improve lighting / focus)")

    else:
        st.error("Upload failed!")
        logger.error("Upload failed!")

if st.session_state.image_id:
    option_map = {
        0: ":material/thumb_up:",
        1: ":material/thumb_down:",
    }
    selection = st.segmented_control(
        "What do you think about this prediction ?",
        options=option_map.keys(),
        format_func=lambda x: option_map[x],
        selection_mode="single",
    )
    if selection == 1:
        st.write(
            "Sorry to hear that! You can always retake the photo with improve lighting / focus"
        )
        handle_failure(st.session_state.image_id)
