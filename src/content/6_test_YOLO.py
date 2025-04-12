import streamlit as st
from ultralytics import YOLO
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
from loguru import logger

st.title("Testing Detection")
model = YOLO(
    "/home/insia/Documents/Projects/target_detector/trarget_detector/train4/weights/best.pt"
)
if "captured_image" not in st.session_state:
    st.session_state.captured_image = None
if "capturing" not in st.session_state:
    st.session_state.capturing = False


def capture_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    logger.debug("callback running")
    if st.session_state.capturing:
        st.session_state.captured_image = img.copy()
        st.session_state.capturing = False
        logger.debug("image in session state")
    return frame


class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.model = YOLO(
            "/home/insia/Documents/Projects/target_detector/trarget_detector/train4/weights/best.pt"
        )
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


rtc_config = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

ctx = webrtc_streamer(
    key="Detect target",
    video_processor_factory=VideoProcessor,
    # rtc_configuration=rtc_config,
    # video_frame_callback=capture_callback,
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
