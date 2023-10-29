import streamlit as st
import ingest


def download_convert_persist():
    twitch_id = st.text_input("Enter Twitch ID")
    st.write(f"You Selected {twitch_id}")

    if st.button("Download"):
        with st.spinner():
            st.write("Downloading...")
            ingest.download_twitch_stream(twitch_id)
            st.write("Converting...")
            ingest.vid_to_frames(twitch_id, use_cuda=False)
            #st.write("Uploading...")
            #r2.upload(twitch_id)
        st.success("Downloaded!")
