from pathlib import Path
import solara
from ipywidgets import Video
import inference

import plotly.express as px

SUPPORTED_FMTS = {"mp4", "avi", "mkv"}


@solara.component()
def Inference():
    file, set_file = solara.use_state(None)
    running_inference, set_running = solara.use_state(False)

    with solara.Details("Select Video", expand=True):
        solara.Select(
            "Select File",
            values=[str(p) for p in Path("converted").glob("*") if p.is_dir()],
            on_value=set_file,
        )

    if file is None:
        solara.Error("Make sure to upload/select file!")
    else:
        solara.Success("File Selected...")
        solara.Button("Run Inference!", on_click=lambda: set_running(True))

    if running_inference:
        solara.Text("Running...")
        solara.ProgressLinear(running_inference)
        df_out = inference.run_inference(Path("resnet_bad.ckpt"), Path(file)).cast({"timestamp": str})  # type: ignore
        solara.FigurePlotly(
            px.line(df_out, x="timestamp", y="preds", line_shape="hv", symbol="preds")
        )
        cutoff, set_cutoff = solara.use_state(1)
        solara.InputFloat("Highlight Y-Cutoff", cutoff, on_value=set_cutoff)

        vid = Video.from_file("1913327876.mp4", format="video/mp4", width=500)
        solara.display(vid)

        solara.FileDownload(lambda: open("1913327876.mp4", "rb"), "vid.mp4")
    # px.line(x=[1, 2, 3], y=[5, 6, 8])
    # px.line(df, x="timestamp", y="preds", line_shape="hv")
    # solara.display(Video.from_file("1913327875.mp4", format="video/mp4"))

    # v = ipywidgets.Video.from_file()
    ...
    pass
