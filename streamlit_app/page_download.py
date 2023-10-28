import streamlit as st
import ingest
import r2


def download_convert_persist():
    def start_download():
        ingest.download_twitch_stream(twitch_id, end_time="00:05:00")
        ingest.vid_to_frames(twitch_id, use_cuda=False)
        r2.upload(twitch_id)

    twitch_id = st.text_input("Enter Twitch ID")
    st.write(f"You Selected {twitch_id}")
    if st.button("Download"):
        with st.spinner():
            start_download()
        st.success("Downloaded!")
