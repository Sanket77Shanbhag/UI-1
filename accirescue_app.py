import streamlit as st
import cv2
import tempfile
import numpy as np
from PIL import Image
import subprocess

# Simulated accident detection function
def detect_accident(frame):
    return np.random.choice([True, False])  # Replace with your ML model

# Function to trigger the SMS notification
def send_notification():
    try:
        subprocess.run(["python", "sms.py"], check=True)
        st.toast("Notification sent to the nearby hospital and police!", icon="✅")
    except Exception as e:
        st.toast(f"Failed to send notification: {e}", icon="⚠️")

# Process uploaded file
def process_file(uploaded_file):
    st.info("Processing file...")
    accident_detected = False

    if uploaded_file.type.startswith("image/"):
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        accident_detected = detect_accident(np.array(image))
    elif uploaded_file.type.startswith("video/"):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(uploaded_file.read())
        cap = cv2.VideoCapture(temp_file.name)

        st.text("Processing video... Hold on!")
        progress_bar = st.progress(0)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        for i in range(frame_count):
            ret, frame = cap.read()
            if not ret:
                break
            if i % 10 == 0:  # Display every 10th frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, caption=f"Processing Frame {i}", use_container_width=True)
            if detect_accident(frame):
                accident_detected = True
                break
            progress_bar.progress((i + 1) / frame_count)
        cap.release()

    if accident_detected:
        st.toast("Accident Detected!", icon="🚨")
        send_notification()
    else:
        st.toast("No Accident Detected.", icon="✔️")

# Main app
def main():
    st.markdown(
        """
        <style>
        .center-title {
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Centered title
    st.markdown('<h1 class="center-title">ACCIRESUE SYSTEM</h1>', unsafe_allow_html=True)
    st.write(
        "The ACCIRESUE SYSTEM is designed to detect accidents in real-time using "
        "live camera feeds or uploaded media. This system uses advanced deep-learning "
        "techniques to identify potential accidents and provide actionable alerts."
    )

    # Go Live Button
    if st.button("Go Live"):
        st.warning("Accessing live camera...")
        cap = cv2.VideoCapture(0)  # Access default webcam
        if not cap.isOpened():
            st.error("Unable to access the camera.")
        else:
            accident_detected = False
            while True:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to read from camera.")
                    break

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame_rgb, caption="Live Camera Feed", use_column_width=True)
                if detect_accident(frame):
                    accident_detected = True
                    st.toast("Accident Detected!", icon="🚨")
                    send_notification()
                    break
            cap.release()

    # Drag and Upload Section
    uploaded_file = st.file_uploader("Drag and drop a video or image for accident detection:", type=["jpg", "jpeg", "png", "mp4", "avi"])
    if uploaded_file is not None:
        process_file(uploaded_file)

# Run the app
if __name__ == "__main__":
    main()
