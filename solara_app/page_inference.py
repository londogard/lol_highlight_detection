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
        # with solara.ColumnsResponsive():
        #    with solara.Column():
        #        solara.Markdown("## Upload File")
        #        solara.FileDrop(lazy=False, on_file=set_file)
        #        solara.Button("Convert")

    if file is None:
        solara.Error("Make sure to upload/select file!")
    else:
        solara.Success("File Selected...")
        solara.Button("Run Inference!", on_click=lambda: set_running(True))

    if running_inference:
        solara.Text("Running...")
        solara.ProgressLinear(running_inference)
        model = inference.load_model(Path("model_newer.pt"))
        df_out = inference.run_inference(model, Path(file))  # type: ignore

        solara.FigurePlotly(px.line(df_out, x="timestamp", y="preds", line_shape="hv"))

        # df = inference.run_inference()
        # import solara.express as px

        # px.line(x=[1, 2, 3], y=[5, 6, 8])
        # px.line(df, x="timestamp", y="preds", line_shape="hv")
        # solara.display(Video.from_file("1913327875.mp4", format="video/mp4"))

    # v = ipywidgets.Video.from_file()
    ...
    pass
