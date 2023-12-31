from pathlib import Path
import polars as pl
import solara
from ipywidgets import Video
from moviepy.editor import VideoFileClip
from solara_app import sol_utils
from solara_app.infer import solara_run_inference
from solara_app.mini_components.c_inference import write_video
from solara_app.mini_components.simple import Progress
from utils import time_slice


MODELS = [str(p) for p in Path("ckpts").rglob("*.ckpt")]


@solara.component
def DfSelector(df: pl.DataFrame, file: str):
    # df = solara.use_reactive(df)

    left = solara.use_reactive(0)
    right = solara.use_reactive(0)
    with solara.Card(style={"justify-content": "center"}):
        cut_off = solara.use_reactive(5)

        sol_utils.CutOffChartSelection(cut_off, df)
        print(cut_off)
        time_df = time_slice.create_start_end_time(df, cut_off.value)
        print("Rendering...")
        time_dict = time_df.cast(pl.Time).cast(pl.Utf8).to_dicts()
        file_name = f"{file.replace('converted', 'downloaded')}.mp4"

        if len(time_dict) == 0:
            solara.Warning("No Highlights available...")
            return

        selected_vid, set_selected_vid = solara.use_state(0)
        tstamp = time_dict[selected_vid]

        res = write_video.use_thread(
            tstamp["start"],
            tstamp["end"],
            selected_vid,
            Path(file_name).stem,
        )
        return

        return
        print(res.value)
        if res.state == solara.ResultState.RUNNING:
            Progress("Building Clip...")
        elif res.state == solara.ResultState.FINISHED:
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
                    disabled=selected_vid == 0,
                    on_click=lambda: set_selected_vid(selected_vid - 1),
                )
                solara.display(vid)
                solara.Button(
                    ">",
                    disabled=selected_vid == (len(time_dict) - 1),
                    on_click=lambda: set_selected_vid(selected_vid + 1),
                )

            with solara.Column(style={"justify-content": "center"}):
                solara.InputInt("Expand Leftwards", left)
                solara.InputInt("Expand Rightwards", right)

                def update_df():
                    if_stmt = pl.when(pl.col("row_nr") == selected_vid)
                    print(time_df.value)
                    time_df.value = (
                        time_df.value.with_row_count()
                        .with_columns(
                            if_stmt.then(
                                (pl.col("start") - pl.duration(seconds=left.value))
                            ).otherwise(pl.col("start")),
                            if_stmt.then(
                                (pl.col("end") + pl.duration(seconds=right.value))
                            ).otherwise(pl.col("end")),
                        )
                        .drop("row_nr")
                    )
                    print(time_df.value)

                with solara.Row():
                    solara.Button(
                        "Remove Video",
                        on_click=lambda: time_df.set(
                            time_df.value.with_columns(active=pl.lit(False))
                        ),
                    )
                    solara.Button(
                        "Remake Video using new settings",
                        color="primary",
                        on_click=update_df,
                    )
                solara.DataFrame(time_df.value.to_pandas())

            solara.Markdown("---")
            solara.Button("Build Full Video", color="primary")


@solara.component
def DfPage(model: str, file: str):
    df = solara_run_inference.use_thread(
        Path(model),
        Path(file),
        aggregate_duration=10,
    )
    print("Rendering..")

    if df is None:
        solara.Markdown("Start running to get further.")
    elif df.state == solara.ResultState.RUNNING:
        Progress("Running...")
    elif df.state == solara.ResultState.FINISHED:
        DfSelector(df.value, file)


@solara.component()
def Inference():
    files = [str(p) for p in Path("converted").glob("*") if p.is_dir()]
    file = solara.use_reactive(files[0])
    model = solara.use_reactive(MODELS[0])
    clicked = solara.use_reactive(False)

    sol_utils.ModelFileSelection(file, model, clicked)
    if clicked.value:
        DfPage(model.value, file.value)

    return

    if clicked.value:
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
        clicked.set(False)
        with solara.Card(style={"justify-content": "center"}):
            cut_off = solara.use_reactive(5)
            sol_utils.CutOffChartSelection(cut_off, df_out.value)

            time_df = solara.use_reactive(
                time_slice.create_start_end_time(
                    df_out.value, cut_off.value
                ).with_columns(active=pl.lit(True))
            )
            print("Rendering...")
            time_dict = time_df.value.cast(pl.Time).cast(pl.Utf8).to_dicts()
            file_name = f"{file.value.replace('converted', 'downloaded')}.mp4"

            if len(time_dict) == 0:
                solara.Warning("No Highlights available...")
                return
            return
            selected_vid, set_selected_vid = solara.use_state(0)
            tstamp = time_dict[selected_vid]

            # use_thread
            vid_clip = VideoFileClip(file_name)

            Path("tmp").mkdir(exist_ok=True)
            clip = vid_clip.subclip(tstamp["start"], tstamp["end"])
            print(time_df.value)

            res = write_video.use_thread(
                clip,
                f"{tstamp['start']}, {tstamp['end']}",
                selected_vid,
                Path(file_name).stem,
            )
            print(res.value)

            if res.state == solara.ResultState.RUNNING:
                Progress("Building Clip...")
            elif res.state == solara.ResultState.FINISHED:
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
                        disabled=selected_vid == 0,
                        on_click=lambda: set_selected_vid(selected_vid - 1),
                    )
                    solara.display(vid)
                    solara.Button(
                        ">",
                        disabled=selected_vid == (len(time_dict) - 1),
                        on_click=lambda: set_selected_vid(selected_vid + 1),
                    )

                with solara.Column(style={"justify-content": "center"}):
                    solara.InputInt("Expand Leftwards", left)
                    solara.InputInt("Expand Rightwards", right)

                    def update_df():
                        if_stmt = pl.when(pl.col("row_nr") == selected_vid)
                        print(time_df.value)
                        time_df.value = (
                            time_df.value.with_row_count()
                            .with_columns(
                                if_stmt.then(
                                    (pl.col("start") - pl.duration(seconds=left.value))
                                ).otherwise(pl.col("start")),
                                if_stmt.then(
                                    (pl.col("end") + pl.duration(seconds=right.value))
                                ).otherwise(pl.col("end")),
                            )
                            .drop("row_nr")
                        )
                        print(time_df.value)

                    with solara.Row():
                        solara.Button(
                            "Remove Video",
                            on_click=lambda: time_df.set(
                                time_df.value.with_columns(active=pl.lit(False))
                            ),
                        )
                        solara.Button(
                            "Remake Video using new settings",
                            color="primary",
                            on_click=update_df,
                        )
                    solara.DataFrame(time_df.value.to_pandas())

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
