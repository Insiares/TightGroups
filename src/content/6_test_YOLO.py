import streamlit as st
from ultralytics import YOLO
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
from loguru import logger
import av


st.title("Testing Detection")
cache_key = "model_cache"
if cache_key in st.session_state:
    import_model = st.session_state[cache_key]
else:
    import_model = YOLO("./target_detector_beta.pt")
    st.session_state[cache_key] = import_model

if "captured_image" not in st.session_state:
    st.session_state.captured_image = None
if "capturing" not in st.session_state:
    st.session_state.capturing = False


def video_callback(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    result = import_model.predict(img, vid_stride=25, verbose=False)
    processed_frame = result[0].plot()
    logger.debug("callback running")
    # if st.session_state.capturing:
    #     st.session_state.captured_image = img.copy()
    #     st.session_state.capturing = False
    #     logger.debug("image in session state")
    return av.VideoFrame.from_ndarray(processed_frame, format="bgr24")


class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.model = import_model
        self.captured_requested = False

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Process with your computer vision model
        result = self.model.predict(img, vid_stride=25, verbose=False, conf=0.95)

        # Draw on the image based on results
        # For example, if your model detects objects, draw bounding boxes:
        # for detection in result.detections:
        #     # Draw bounding box
        #     x, y, w, h = detection.bbox
        #     cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        #
        #     # Add label
        #     cv2.putText(img, detection.label, (x, y-10),
        #                 cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
        return frame.from_ndarray(result[0].plot())


#


# rtc_config = RTCConfiguration(
#     {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
# )

ctx = webrtc_streamer(
    key="Detect target",
    video_processor_factory=VideoProcessor,
    # rtc_configuration=rtc_config,
    # mode = WebRtcMode.SENDRECV,
    # video_frame_callback=video_callback,
    # async_processing=True,
    media_stream_constraints={"video": True, "audio": False},
)


if ctx.state.playing:
    if st.button("Take a picture"):
        logger.debug("button lcicked")
        st.session_state.capturing = True
        st.rerun()


if st.session_state.captured_image is not None:
    img = st.session_state.captured_image
    st.image(img)

st.write(f"Capturing : {st.session_state.capturing}")
st.write(f"Captured image : {st.session_state.captured_image}")
