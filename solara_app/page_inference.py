from collections import defaultdict
from pathlib import Path
import polars as pl
import solara
from ipywidgets import Video
from moviepy.editor import VideoFileClip
from solara_app import sol_utils
from solara_app.infer import solara_run_inference
from solara_app.mini_components.c_inference import write_full_video, write_video
from solara_app.mini_components.simple import Progress
from utils import time_slice


MODELS = [str(p) for p in Path("ckpts").rglob("*.ckpt")]


def false() -> bool:
    return False


@solara.component
def DfSelector(df: pl.DataFrame, file: str):
    extend_forward = solara.use_reactive({})
    extend_backward = solara.use_reactive({})
    disabled = solara.use_reactive({})
    selected_vid, set_selected_vid = solara.use_state(0)
    cut_off = solara.use_reactive(5)
    clicks = solara.use_reactive(0)

    with solara.Card(style={"justify-content": "center"}):
        sol_utils.CutOffChartSelection(cut_off, df)
        time_df = time_slice.create_start_end_time(
            df, cut_off.value, extend_forward.value, extend_backward.value
        )

        print("Rendering...")
        time_dict = time_df.cast(pl.Time).cast(pl.Utf8).to_dicts()
        time_dict = solara.use_reactive(time_dict)
        file_name = f"{file.replace('converted', 'downloaded')}.mp4"

        if len(time_dict.value) == 0:
            solara.Warning("No Highlights available...")
            return

        tstamp = time_dict.value[selected_vid]

        res = write_video.use_thread(
            tstamp["start"],
            tstamp["end"],
            selected_vid,
            Path(file_name).stem,
        )

        if res.state == solara.ResultState.RUNNING:
            Progress("Building Clip...")
        elif res.state == solara.ResultState.FINISHED:
            vid = Video.from_file(res.value, width=500, autoplay=False, loop=False)
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
                    disabled=selected_vid == (len(time_dict.value) - 1),
                    on_click=lambda: set_selected_vid(selected_vid + 1),
                )

            with solara.Column(style="justify-content: center"):
                with solara.Row(style={"justify-content": "center"}):
                    solara.InputInt(
                        "Expand Leftwards (s)",
                        value=extend_backward.value.get(selected_vid, 0),
                        on_value=lambda v: extend_backward.set(
                            {**extend_backward.value, selected_vid: v}
                        ),
                    )
                    solara.InputInt(
                        "Expand Rightwards (s)",
                        value=extend_forward.value.get(selected_vid, 0),
                        on_value=lambda v: extend_forward.set(
                            {**extend_forward.value, selected_vid: v}
                        ),
                    )

                def disable_vid(vid: int):
                    return lambda: disabled.set(
                        {**disabled.value, vid: not disabled.value.get(vid)}
                    )

                solara.Button(
                    "Add Video" if disabled.value.get(selected_vid) else "Remove Video",
                    on_click=disable_vid(selected_vid),
                    style={"width": "25%"},
                )

            solara.Markdown("---")

            solara.Button(
                "Build Full Video",
                color="primary",
                on_click=lambda: clicks.set(clicks.value + 1),
            )

            if clicks.value > 0:
                res_full = write_full_video.use_thread(
                    time_dict.value,
                    disabled.value,
                    Path(file_name).stem,
                    str(time_dict),
                )
                if res_full.state == solara.ResultState.RUNNING:
                    Progress("Building Full Clip...")
                elif res_full.state == solara.ResultState.FINISHED:
                    solara.FileDownload(
                        lambda: open(res_full.value, "rb"), Path(res_full.value).name
                    )


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
