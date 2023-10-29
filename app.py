import streamlit as st
from streamlit_app import page_inference

from streamlit_app.page_download import download_convert_persist


def sidebar():
    with st.sidebar:
        r2_config = st.file_uploader("Upload R2 Config")
        if r2_config is not None:
            open("rclone.conf", "w").write(r2_config)


def main():
    sidebar()
    st.header("League of Legend Highlight Extractor")
    mode = st.selectbox("Select Mode", ["Inference", "Download, Convert and Persist Twitch Clips"])

    if mode == "Download, Convert and Persist Twitch Clips":
        download_convert_persist()
    else:
        page_inference.inference_page()


if __name__ == "__main__":
    main()
