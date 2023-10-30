from pathlib import Path
import shutil
from networkx import is_empty
import streamlit as st
import r2
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
    if len(list(Path("ckpts").glob("*"))) == 0:
        with st.spinner():
            r2.download("models/ckpts/timm/tf_efficientnet_b3.aa_in1k.ckpt")
            shutil.move("tf_efficientnet_b3.aa_in1k.ckpt", "ckpts/timm")
    mode = st.selectbox("Select Mode", ["Inference", "Download, Convert and Persist Twitch Clips"])

    if mode == "Download, Convert and Persist Twitch Clips":
        download_convert_persist()
    else:
        page_inference.inference_page()


if __name__ == "__main__":
    main()
