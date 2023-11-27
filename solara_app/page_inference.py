import datetime
from pathlib import Path
from typing import Optional
import polars as pl
import solara
from ipywidgets import Video

import plotly.express as px
from solara_app.infer import convert_vid, solara_run_inference
from utils import time_slice

from utils.movie_clips import build_video, get_vid_path

MODELS = [str(p) for p in Path("ckpts").rglob("*.ckpt")]


@solara.component()
def Inference():
    files = [str(p) for p in Path("converted").glob("*") if p.is_dir()]
    file, set_file = solara.use_state(files[0])
    model, set_model = solara.use_state(MODELS[0])
    df, set_df = solara.use_state(None)
    clicked, set_clicked = solara.use_state(False)

    with solara.Details("Select Video", expand=True):
        solara.Select(
            "Select File",
            values=files,
            value=file,
            on_value=set_file,
        )
        solara.Select(
            "Select Model",
            values=MODELS,
            value=model,
            on_value=set_model,
        )
        solara.Button(
            "Run Inference!",
            color="primary",
            on_click=lambda: set_clicked(True),
        )
    if clicked:
        set_df(
            solara_run_inference.use_thread(
                Path(model),
                Path(file),
                aggregate_duration=10,
            )
        )

    if df is None:
        solara.Markdown("Start running to get further.")
    elif df.state == solara.ResultState.RUNNING:
        solara.Markdown("Running...")
        solara.ProgressLinear(True)
    elif df.state == solara.ResultState.FINISHED:
        df_out: pl.DataFrame = df.value
        with solara.Card():
            row = solara.Row()

            cut_off, set_cutoff = solara.use_state(5)
            solara.SliderInt(
                "Highlight Y-Cutoff",
                cut_off,
                min=df_out["preds"].min() + 1,
                max=df_out["preds"].max() + 1,
                on_value=set_cutoff,
            )
            with row:
                fig = px.line(
                    df_out.cast({"timestamp": str}),
                    x="timestamp",
                    y="preds",
                    line_shape="hv",
                )
                fig.add_hline(y=cut_off, line_color="red")
                solara.FigurePlotly(fig)

            df = time_slice.create_start_end_time(df_out, cut_off)
            time_dict = time_slice.merge_overlaps_into_dict(df)

            file_name = f"{file.replace('converted', 'downloaded')}.mp4"
            higlight_vid = get_vid_path(
                file_name,
                time_dict,
                Path("highlights"),
            )

            convert, set_convert = solara.use_state(False)
            solara.Button(
                "Create highlight Video",
                color="primary",
                on_click=lambda: set_convert(True),
            )
            if convert:
                out_vid = convert_vid.use_thread(file_name, time_dict, higlight_vid)
                if out_vid.state == solara.ResultState.RUNNING:
                    solara.Markdown("")
                    solara.ProgressLinear(True)
                elif out_vid.state == solara.ResultState.FINISHED:
                    vid = Video.from_file(
                        str(higlight_vid), format="video/mp4", width=500
                    )
                    solara.display(vid)

                    solara.FileDownload(
                        lambda: open(str(higlight_vid), "rb"), "vid.mp4"
                    )
