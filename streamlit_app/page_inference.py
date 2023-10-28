from pathlib import Path
import inference

import plotly.express as px
import streamlit as st

from utils.movie_clips import build_video


def inference_page():
    with st.expander("Select Video", expanded=True):
        selected_file = st.selectbox(
            "Select File", [str(p) for p in Path("converted").glob("*") if p.is_dir()]
        )

    if selected_file is None:
        st.error("Make sure to upload/select file!")
        st.stop()

    st.success("File Selected...")

    df_out = inference.run_inference(
        Path("resnet_bad.ckpt"), Path(selected_file), aggregate_duration=10
    )
    chart_container = st.container()
    cut_off = st.slider(
        "Y-Cutoff Highlight",
        min_value=df_out["preds"].min(),
        max_value=df_out["preds"].max() + 1,
    )
    buffer = st.slider("Buffering", -5, 5, value=0, step=1)

    fig = px.line(df_out, x="timestamp", y="preds", line_shape="hv", symbol="preds")
    fig.add_hline(cut_off, line_color="red", line_dash="dash")
    with chart_container:
        st.plotly_chart(fig)
    import polars as pl

    df = df_out.filter(pl.col("preds").rolling_max(2) > cut_off)["timestamp"]
    # TODO: merge similars

    build_video(
        "1913327876.mp4",
        [
            {"start": "00:00:00", "end": "00:00:01"},
            {"start": "00:00:04", "end": "00:00:05"},
        ],
        Path("out.mp4"),
    )
    st.video("out.mp4")
    st.write("Right Click to Download")
