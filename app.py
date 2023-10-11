from pathlib import Path
import solara
import solara.lab
import ingest
import r2
import ipywidgets


@solara.component()
def DownloadConvertPersist():
    twitch_id, set_twitch_id = solara.use_state("")
    is_downloading, set_downloading = solara.use_state(False)
    status, set_status = solara.use_state("")

    def start_download():
        set_downloading(True)
        set_status("")
        ingest.download_twitch_stream(twitch_id, end_time="00:05:00")
        ingest.vid_to_frames(twitch_id, use_cuda=False)
        r2.upload(twitch_id)
        set_status("Download completed")
        set_downloading(False)

    solara.InputText(
        "Select Twitch ID", twitch_id, set_twitch_id, disabled=is_downloading
    )
    solara.Markdown(f"You Selected {twitch_id}")
    solara.Button("Download", start_download, disabled=is_downloading)
    solara.ProgressLinear(is_downloading)
    solara.Text(status)


@solara.component()
def DatasetR2():
    twitch_id, set_twitch_id = solara.use_state("")
    is_downloading, set_downloading = solara.use_state(False)
    status, set_status = solara.use_state("")

    solara.Button("Download all data from R2", color="green")


@solara.component()
def Inference():
    file, set_file = solara.use_state(None)
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
        solara.Button("Run Inference!")

        # v = ipywidgets.Video.from_file()

    pass


@solara.component()
def Page():
    with solara.Sidebar():
        solara.Title("League of Legend Highlight Extractor")
        solara.FileDrop(
            label="Drop R2 Config",
            lazy=False,
            on_file=lambda x: open("rclone.conf", "wb").write(x["data"]),
        )
    if not Path("rclone.conf").exists():
        solara.Error("Upload rclone.conf first!")

    with solara.lab.Tabs():
        with solara.lab.Tab("Inference"):
            Inference()
        with solara.lab.Tab("Download, Convert and Persist Twitch Clips"):
            DownloadConvertPersist()


Page()
