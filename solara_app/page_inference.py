import solara
from ipywidgets import Video


SUPPORTED_FMTS = {"mp4", "avi", "mkv"}


@solara.component()
def DownloadTwitch():
    solara.Text("To be implemented..")



@solara.component()
def Inference():
    file, set_file = solara.use_state(None)
    running_inference, set_running = solara.use_state(False)

    with solara.Details("Select Video", expand=True):
        with solara.ColumnsResponsive():
            with solara.Column():
                solara.Markdown("## Upload File")
                solara.FileDrop(lazy=False, on_file=set_file)
                solara.Button("Convert")
            with solara.Column():
                solara.Markdown("## Download from Twitch")
                twitch, set_twitch = solara.use_state("")
                solara.InputText("Select Twitch ID", value=twitch, on_value=set_twitch)
                solara.Button(f"Download {twitch}!")

    if file is None:
        solara.Error("Make sure to upload/select file!")
    elif file["name"].rsplit(".", 1)[1] not in SUPPORTED_FMTS:
        solara.Error(f"Invalid file type - only {SUPPORTED_FMTS} supported!")
        file = None
    else:
        solara.Success("File Selected...")
        solara.Button("Run Inference!", on_click=lambda: set_running(True))
    
    if running_inference:
        solara.Text("Running...")
        solara.ProgressLinear(running_inference)
        solara.display(Video.from_file("1913327875.mkv"))
        # df = inference.run_inference()
        # import solara.express as px

        # px.line(x=[1, 2, 3], y=[5, 6, 8])
        # px.line(df, x="timestamp", y="preds", line_shape="hv")

    # v = ipywidgets.Video.from_file()
    ...
    pass