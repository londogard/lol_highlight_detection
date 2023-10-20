import solara
from ipywidgets import Video


@solara.component()
def Inference():
    file, set_file = solara.use_state(None)
    running_inference, set_running = solara.use_state(False)
    with solara.Details("Select Video", expand=True):
        with solara.Details("Upload Video"):
            solara.FileDrop(lazy=False, on_file=set_file)
            solara.Button("Convert")
        with solara.Details("Download Twitch Video"):
            solara.InputText("Select Twitch ID")
            solara.Button("Download!")

    if file is None:
        solara.Error("Make sure to upload/select file!")
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