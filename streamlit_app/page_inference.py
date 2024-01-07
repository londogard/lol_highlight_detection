import datetime
from pathlib import Path
import inference

import plotly.express as px
import streamlit as st
import polars as pl
from utils import time_slice
from utils.movie_clips import build_video, get_vid_path


@st.cache_data
def st_run_inference(
    model_path: Path,
    image_folder: Path,
    aggregate_duration: int = 30,
    fps: int = 3,
) -> pl.DataFrame:
    return inference.run_inference(model_path, image_folder, aggregate_duration, fps)


def inference_page():
    with st.form("random"):
        selected_file = st.selectbox(
            "Select File", [str(p) for p in Path("converted").glob("*") if p.is_dir()]
        )
        selected_model = st.selectbox(
            "Select Model", [str(p) for p in Path("ckpts").rglob("*.ckpt")]
        )
        st.form_submit_button("Extract Highlights!")

    df_out = st_run_inference(
        Path(selected_model),
        Path(selected_file),
        aggregate_duration=10,
    )
    chart_container = st.container()
    cut_off = st.slider(
        "Y-Cutoff Highlight",
        min_value=df_out["preds"].min() + 1,
        max_value=df_out["preds"].max() + 1,
    )
    with st.expander("Advanced Options"):
        st.write("Non available right now.")

    fig = px.line(df_out, x="timestamp", y="preds", line_shape="hv")
    fig.add_hline(cut_off, line_color="red", line_dash="dash")
    with chart_container:
        st.plotly_chart(fig)

    df = time_slice.create_start_end_time(df_out, cut_off)
    times_dict = time_slice.merge_overlaps_into_dict(df)
    # event: datetime.time = st.select_slider(
    #    "Validate event", options=[x["start"] for x in times_dict]
    # )

    higlight_vid = get_vid_path(
        f"{selected_file.replace('converted', 'downloaded')}.mp4",
        times_dict,
        Path("highlights"),
    )

    if st.button("Create highlight Video"):
        with st.spinner("Creating video..."):
            build_video(
                f"{selected_file.replace('converted', 'downloaded')}.mp4",
                times_dict,
                higlight_vid,
            )

    if higlight_vid.exists():
        st.video(str(higlight_vid))
        st.info("Right Click to Download", icon="ℹ️")
