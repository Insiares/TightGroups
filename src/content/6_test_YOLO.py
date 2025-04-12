import streamlit as st 
import cv2
from ultralytics import YOLO
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import numpy as np
import threading
import queue
from loguru import logger

st.title("Testing Detection")
model = YOLO("/home/insia/Documents/Projects/target_detector/trarget_detector/train4/weights/best.pt")

result_queue = queue.Queue()
logger.debug(f"result_queue : {result_queue.empty()}")
if "captured_image" not in st.session_state:
    st.session_state.captured_image = None


class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.model =  YOLO("/home/insia/Documents/Projects/target_detector/trarget_detector/train4/weights/best.pt")
        self.captured_requested = False
        self.result_queue = result_queue

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Process with your computer vision model
        result = self.model.predict(img, vid_stride = 25, verbose = False)
        
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
        if self.captured_requested:
            self.result_queue.put(img.copy())
            logger.debug("capture in queue")
            self.captured_requested = False
        return frame.from_ndarray(result[0].plot())
#
    def request_capture(self):
        logger.debug("capture requested") 
        self.captured_requested = True


rtc_config = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

ctx = webrtc_streamer(
    key="Detect target",
    video_processor_factory=VideoProcessor,
    rtc_configuration=rtc_config,
    async_processing=True,
    media_stream_constraints={"video": True, "audio": False}
)


if ctx.video_processor:
    if st.button("Take a picture"):
        ctx.video_processor.request_capture()
        
        if not ctx.video_processor.result_queue.empty():
            st.session_state.captured_image = result_queue.get_nowait()
st.write(st.session_state.captured_image)
if st.session_state.captured_image is not None:
    st.image(st.session_state.captured_image)
