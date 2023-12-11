from pathlib import Path
import time
import polars as pl
import solara
from ipywidgets import Video
from moviepy.editor import VideoFileClip
import plotly.express as px
from solara_app import sol_utils
from solara_app.infer import solara_run_inference
from solara_app.mini_components.c_inference import write_video
from solara_app.mini_components.simple import Progress
from utils import time_slice


def update_df(
    df: solara.Reactive[pl.DataFrame], selected_vid: int, left: int, right: int
):
    if_stmt = pl.when(pl.col("row_nr") == selected_vid)
    print(df.value)
    df.value = (
        df.value.with_row_count()
        .with_columns(
            if_stmt.then((pl.col("start") - pl.duration(seconds=left))).otherwise(
                pl.col("start")
            ),
            if_stmt.then((pl.col("end") + pl.duration(seconds=right))).otherwise(
                pl.col("end")
            ),
        )
        .drop("row_nr")
    )
    print(df.value)


@solara.component()
def Inference():
    file = solara.use_reactive(sol_utils.FILES[0])
    model = solara.use_reactive(sol_utils.MODELS[0])
    df, set_df = solara.use_state(None)
    clicked, set_clicked = solara.use_state(False)
    left = solara.use_reactive(0)
    right = solara.use_reactive(0)
    use_clip = solara.use_reactive(True)

    selected_vid = solara.use_reactive(0)
    cut_off = solara.use_reactive(5)

    sol_utils.ModelFileSelection(file, model, set_clicked)
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
            sol_utils.cut_off_chart(cut_off, df_out.use_value())
            time_df = solara.use_reactive(
                time_slice.create_start_end_time(df_out.use_value(), cut_off.value)
            )

            time_dict = time_df.value.cast(pl.Time).cast(pl.Utf8).to_dicts()
            file_name = f"{file.value.replace('converted', 'downloaded')}.mp4"

            if len(time_dict) == 0:
                solara.Warning("No Highlights available...")
                return

            tstamp = time_dict[selected_vid.value]

            # use_thread
            vid_clip = VideoFileClip(file_name)

            Path("tmp").mkdir(exist_ok=True)
            clip = vid_clip.subclip(tstamp["start"], tstamp["end"])
            res = write_video.use_thread(
                clip,
                f"{tstamp['start']}, {tstamp['end']}",
                selected_vid.value,
                Path(file_name).stem,
            )
            print("Rendering...")
            if res.state == solara.ResultState.RUNNING:
                Progress("Building Clip...")
            if res.state == solara.ResultState.FINISHED:
                vid = Video.from_file(res.value, width=500)
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
                    solara.InputInt("Expand Leftwards", left)
                    solara.InputInt("Expand Rightwards", right)

                    with solara.Row():
                        solara.Button(
                            "Remove Video", on_click=lambda: use_clip.set(False)
                        )
                        solara.Button(
                            "Remake Video using new settings",
                            color="primary",
                            on_click=lambda: update_df(
                                time_df,
                                selected_vid.use_value(),
                                left.use_value(),
                                right.use_value(),
                            ),
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
