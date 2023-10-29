import datetime
from pathlib import Path
import inference

import plotly.express as px
import streamlit as st

from utils.movie_clips import build_video


def inference_page():
    with st.form("random"):
        selected_file = st.selectbox(
            "Select File", [str(p) for p in Path("converted").glob("*") if p.is_dir()]
        )
        st.form_submit_button("Extract Highlights!")
    df_out = inference.run_inference(
        Path("hf_hub:timm/tf_efficientnet_b3.aa_in1k.ckpt"), Path(selected_file), aggregate_duration=10
    )
    chart_container = st.container()
    cut_off = st.slider(
        "Y-Cutoff Highlight",
        min_value=df_out["preds"].min() + 1,
        max_value=df_out["preds"].max() + 1,
    )
    # buffer = st.slider("Buffering", 0, 15, value=0, step=1)

    fig = px.line(df_out, x="timestamp", y="preds", line_shape="hv")
    fig.add_hline(cut_off, line_color="red", line_dash="dash")
    with chart_container:
        st.plotly_chart(fig)
    import polars as pl

    df = df_out.filter(pl.col("preds") >= cut_off).select(
        start=pl.col("timestamp"),
        end=(pl.date(2023,1, 1).dt.combine(pl.col("timestamp")) + datetime.timedelta(seconds=10)).dt.time())
    
    data = df.cast(pl.Utf8).to_dicts()
    new_data = [data[0]]
    for row in data[1:]:
        if new_data[-1]["end"] == row["start"]:
            new_data[-1]["end"] = row["end"]
        else:
            new_data.append(row)

    higlight_vid = build_video(
        f"{selected_file.replace('converted', 'downloaded')}.mp4",
        new_data[7:15], 
        Path("highlights"),
    )

    st.video(str(higlight_vid))
    st.write("Right Click to Download")
