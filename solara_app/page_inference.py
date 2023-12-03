import datetime
from pathlib import Path
from sre_constants import SUCCESS
import time
from typing import Optional
import polars as pl
import solara
from ipywidgets import Video
from moviepy.editor import VideoFileClip
import plotly.express as px
from solara_app.infer import convert_vid, solara_run_inference
from solara_app.mini_components.c_inference import write_video
from solara_app.mini_components.simple import Progress
from utils import time_slice

from utils.movie_clips import build_video, get_vid_path

MODELS = [str(p) for p in Path("ckpts").rglob("*.ckpt")]


@solara.component()
def Inference():
    files = [str(p) for p in Path("converted").glob("*") if p.is_dir()]
    file = solara.use_reactive(files[0])
    model = solara.use_reactive(MODELS[0])
    df, set_df = solara.use_state(None)
    clicked, set_clicked = solara.use_state(False)
    left = solara.use_reactive(0)
    right = solara.use_reactive(0)
    use_clip = solara.use_reactive(True)

    with solara.Details("Select Video", expand=True):
        solara.Select(
            "Select File",
            values=files,
            value=file,
        )
        solara.Select(
            "Select Model",
            values=MODELS,
            value=model,
        )
        solara.Button(
            "Run Inference!",
            color="primary",
            on_click=lambda: set_clicked(True),
        )
    if clicked:
        set_df(
            solara_run_inference.use_thread(
                Path(model.value),
                Path(file.value),
                aggregate_duration=10,
            )
        )

    if df is None:
        solara.Markdown("Start running to get further.")
    elif df.state == solara.ResultState.RUNNING:
        Progress("Running...")
    elif df.state == solara.ResultState.FINISHED:
        df_out: solara.Reactive[pl.DataFrame] = solara.use_reactive(df.value)

        with solara.Card(style={"justify-content": "center"}):
            row = solara.Row()

            cut_off = solara.use_reactive(5)
            solara.SliderInt(
                "Highlight Y-Cutoff",
                cut_off,
                min=df_out.value["preds"].min() + 1,
                max=df_out.value["preds"].max(),
                thumb_label="always",
                tick_labels="end_points",
            )
            with row:
                fig = px.line(
                    df_out.value.cast({"timestamp": str}),
                    x="timestamp",
                    y="preds",
                    line_shape="hv",
                )
                fig.add_hline(y=cut_off.value, line_color="red")
                solara.FigurePlotly(fig)

            time_df = solara.reactive(
                time_slice.create_start_end_time(df_out.value, cut_off.value)
            )
            time_dict = time_slice.merge_overlaps_into_dict(time_df.value)
            file_name = f"{file.value.replace('converted', 'downloaded')}.mp4"

            if len(time_dict) == 0:
                solara.Warning("No Highlights available...")
                return

            selected_vid = solara.use_reactive(0)
            tstamp = time_dict[selected_vid.value]
            # use_thread
            vid_clip = VideoFileClip(file_name)

            Path("tmp").mkdir(exist_ok=True)
            clip = vid_clip.subclip(tstamp["start"], tstamp["end"])
            res = write_video.use_thread(clip, selected_vid.value, Path(file_name).stem)

            if res.state == solara.ResultState.RUNNING:
                Progress("Building Clip...")
            if res.state == solara.ResultState.FINISHED:
                time.sleep(0.1)
                vid = Video.from_file(f"tmp/{selected_vid.value}.mp4", width=500)
                with solara.Row(
                    style={
                        "justify-content": "center",
                        "align-items": "center;",
                        "float": "bottom",
                    }
                ):
                    solara.Button(
                        "<",
                        disabled=selected_vid.value == 0,
                        on_click=lambda: selected_vid.set(selected_vid.value - 1),
                    )
                    solara.display(vid)
                    solara.Button(
                        ">",
                        disabled=selected_vid.value == (len(time_dict) - 1),
                        on_click=lambda: selected_vid.set(selected_vid.value + 1),
                    )

                with solara.Column(style={"justify-content": "center"}):
                    # solara.Checkbox(label="Include Clip?", value=use_clip)
                    solara.InputInt("Expand Leftwards", left)
                    solara.InputInt("Expand Rightwards", right)
                    solara.display(time_df.value.dtypes)

                    def update_df():
                        if_stmt = pl.when(pl.col("row_nr") == selected_vid.value)
                        time_df.value = (
                            time_df.value.with_row_count()
                            .with_columns(
                                if_stmt.then(pl.col("start") - left.value).otherwise(
                                    pl.col("start")
                                ),
                                if_stmt.then(pl.col("end") + left.value).otherwise(
                                    pl.col("end")
                                ),
                            )
                            .drop("row_nr")
                        )

                    with solara.Row():
                        solara.Button(
                            "Remove Video", on_click=lambda: use_clip.set(False)
                        )
                        solara.Button(
                            "Remake Video using new settings",
                            color="primary",
                            on_click=update_df,
                        )

                solara.Markdown("---")
                solara.Button("Build Full Video", color="primary")

            # if convert:
            # video = VideoFileClip(file_name)
            # Path("tmp").mkdir(exist_ok=True)
            # for i, highlight in enumerate(time_dict):
            # clip = video.subclip(highlight["start"], highlight["end"])
            # clip.write_videofile(f"tmp/{i}.mp4")
            # vid = Video.from_file(str("tmp/1.mp4"), format="video/mp4", width=500)
            # vid.set_state()
            # solara.display(vid)
            """higlight_vid = get_vid_path(
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
                imgs = list(Path(file).glob("*.jpg"))
                solara.SliderValue("Subclip", value=time_dict[0], values=time_dict)
                solara.Image(imgs[0])
                pass
            if False:  # convert:
                out_vid = convert_vid.use_thread(file_name, time_dict, higlight_vid)
                if out_vid.state == solara.ResultState.RUNNING:
                    Progress("Building Video...")
                elif out_vid.state == solara.ResultState.FINISHED:
                    vid = Video.from_file(
                        str(higlight_vid), format="video/mp4", width=500
                    )
                    # vid.set_state()
                    solara.display(vid)

                    solara.FileDownload(
                        lambda: open(str(higlight_vid), "rb"), "vid.mp4"
                    )
            """
