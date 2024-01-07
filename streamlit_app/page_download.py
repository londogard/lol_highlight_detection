import json
from pathlib import Path
import subprocess
import streamlit as st
import ingest
from utils import kick_dl


def download_convert_persist():
    service = st.radio("Streaming service", ["Twitch", "Kick"])
    if service == "Twitch":
        twitch_id = st.text_input("Enter Twitch ID")
        st.write(f"You Selected {twitch_id}")

        if st.button("Download"):
            with st.spinner():
                st.write("Downloading...")
                ingest.download_twitch_stream(twitch_id)
                st.write("Converting...")
                ingest.vid_to_frames(twitch_id, use_cuda=False)
            st.success("Downloaded!")

    elif service == "Kick":
        kick_id = st.text_input("Enter Kick ID")
        name = st.text_input("Nickname of video")
        kick_id = Path(kick_id).name
        API_PATH = "https://kick.com/api/v1/video/"
        st.write(f"Open [this]({API_PATH}{kick_id}) and copy text into the box below.")
        json_data = st.text_input("Copy and paste here.")
        if len(json_data):
            json_data = json.loads(json_data)["source"]

            if st.button("Download"):
                with st.spinner():
                    st.write("Downloading...")
                    if not Path(f"converted/{name}").exists():
                        subprocess.Popen(
                            [
                                "ffmpeg",
                                "-i",
                                json_data,
                                "-vcodec",
                                "copy",
                                "-acodec",
                                "copy",
                                f"downloaded/{name}.mp4",
                            ]
                        )

                        st.write("Converting...")
                        ingest.vid_to_frames(name, use_cuda=False)
                        Path(f"downloaded/{name}.mp4").unlink()

                st.success("Downloaded!")
