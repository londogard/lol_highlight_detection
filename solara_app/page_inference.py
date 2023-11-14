import datetime
from pathlib import Path
import solara
from ipywidgets import Video

import plotly.express as px
from solara_app.infer import solara_run_inference

from utils.movie_clips import build_video, get_vid_path

MODELS = [str(p) for p in Path("ckpts").rglob("*.ckpt")]


@solara.component()
def Inference():
    files = [str(p) for p in Path("converted").glob("*") if p.is_dir()]
    file, set_file = solara.use_state(files[0])
    model, set_model = solara.use_state(MODELS[0])
    running_inference, set_running = solara.use_state(False)

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
            "Run Inference!", color="primary", on_click=lambda: set_running(True)
        )

    with solara.Card():
        if running_inference:
            solara.Text("Running...")

            df_out = solara_run_inference.use_thread(
                Path(model),
                Path(file),
                aggregate_duration=10,
            )
            if df_out.state == solara.ResultState.RUNNING:
                solara.ProgressLinear(True)
            if df_out.state == solara.ResultState.FINISHED:
                df_out = df_out.value  # type: ignore
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
                import polars as pl

                df = df_out.filter(pl.col("preds") >= cut_off).select(
                    start=pl.col("timestamp"),
                    end=(
                        pl.date(2023, 1, 1).dt.combine(pl.col("timestamp"))
                        + datetime.timedelta(seconds=10)
                    ).dt.time(),
                )

                data = df.cast(pl.Utf8).to_dicts()
                new_data = [data[0]]
                for row in data[1:]:
                    if new_data[-1]["end"] == row["start"]:
                        new_data[-1]["end"] = row["end"]
                    else:
                        new_data.append(row)

                file_name = f"{file.replace('converted', 'downloaded')}.mp4"
                higlight_vid = get_vid_path(
                    file_name,
                    new_data,
                    Path("highlights"),
                )
                solara.Button(
                    "Create highlight Video",
                    color="primary",
                    on_click=lambda: build_video(file_name, new_data, higlight_vid),
                )

                if higlight_vid.exists():
                    vid = Video.from_file(
                        str(higlight_vid), format="video/mp4", width=500
                    )
                    solara.display(vid)

                    solara.FileDownload(
                        lambda: open(str(higlight_vid), "rb"), "vid.mp4"
                    )
