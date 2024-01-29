from pathlib import Path
import polars as pl
import solara

from solara_app import sol_utils
from solara_app.css import ALIGN_CENTER, JUSTIFY_CENTER
from solara_app.folders import CHECKPOINTS, CONVERTED
from solara_app.infer import solara_run_inference
from solara_app.mini_components.c_inference import write_full_video, write_video
from solara_app.mini_components.simple import Progress, ProgressDynamic, Video
from utils import time_slice


def false() -> bool:
    return False


@solara.component
def DfSelectComponent(df: pl.DataFrame, file: str):
    extend_forward = solara.use_reactive({})
    extend_backward = solara.use_reactive({})
    disabled = solara.use_reactive({})
    selected_vid, set_selected_vid = solara.use_state(0)
    cut_off = solara.use_reactive(5)
    clicks, set_clicks = solara.use_state(0)

    with solara.Card(
        "Highlight Selection & Editing",
        "Select highlight threshold, remove or expand clips",
    ):
        sol_utils.CutOffChartSelection(cut_off, df)

        time_df = time_slice.create_start_end_time(
            df, cut_off.value, extend_forward.value, extend_backward.value
        )

        time_dict = time_df.select(pl.all().dt.strftime("%H:%M:%S")).to_dicts()
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

        ProgressDynamic("Building Clip...", res)

        # TODO: extract into component.
        if res.state == solara.ResultState.FINISHED:
            with solara.Row(style={**JUSTIFY_CENTER, **ALIGN_CENTER}):
                solara.Button(
                    "<",
                    disabled=selected_vid == 0,
                    on_click=lambda: set_selected_vid(selected_vid - 1),
                )
                Video(res.value)
                solara.Button(
                    ">",
                    disabled=selected_vid == (len(time_dict.value) - 1),
                    on_click=lambda: set_selected_vid(selected_vid + 1),
                )

            with solara.Column(style=JUSTIFY_CENTER):
                with solara.Row(style=JUSTIFY_CENTER):
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
                    "✅ Add Video"
                    if disabled.value.get(selected_vid)
                    else "❌ Remove Video",
                    on_click=disable_vid(selected_vid),
                    style={"width": "25%"},
                )

        with solara.Card("Full Video", "Build the full video!"):
            solara.Button(
                "Build Full Video",
                color="primary",
                on_click=lambda: set_clicks(clicks + 1),
            )

            if clicks > 0:
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
def ShowDfComponent(model: str, file: str):
    df = solara_run_inference.use_thread(
        Path(model),
        Path(file),
        aggregate_duration=10,
    )

    if df.state == solara.ResultState.RUNNING:
        Progress("Running...")
    elif df.state == solara.ResultState.FINISHED:
        DfSelectComponent(df.value, file)


@solara.component()
def Inference():
    files = [str(p) for p in CONVERTED.glob("*") if p.is_dir()]
    models = [str(p) for p in CHECKPOINTS.rglob("*.ckpt")]
    file = solara.use_reactive(files[0] if len(files) else None)
    model = solara.use_reactive(models[0] if len(models) else None)

    if model.value is None or file.value is None:
        return solara.Markdown(
            "**It's required to at least download one stream and have one model available!**"
        )

    clicked = solara.use_reactive(False)

    sol_utils.ModelFileSelectComponent(file, model, clicked)

    if clicked.value:
        ShowDfComponent(model.value, file.value)
    else:
        solara.Markdown("**Start running to get further. 🚀**")
