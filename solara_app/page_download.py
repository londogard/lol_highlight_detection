import datetime
import solara
import torch
import ingest
import r2
from solara_app.mini_components.simple import Progress


@solara.component()
def DownloadConvertPersist():
    twitch_id = solara.use_reactive("")
    is_downloading, set_downloading = solara.use_state(False)
    status, set_status = solara.use_state("")
    end_time = solara.use_reactive(None)

    def start_download():
        set_downloading(True)
        set_status("")
        ingest.download_twitch_stream(twitch_id.value, end_time=end_time.value)
        ingest.vid_to_frames(twitch_id.value, use_cuda=torch.cuda.is_available())

        set_status("Download completed")
        set_downloading(False)

    solara.InputText("Select Twitch ID", twitch_id, disabled=is_downloading)
    solara.InputText("End Time (hh:mm:ss)", end_time)

    solara.Markdown(f"You Selected {twitch_id.value}")
    solara.Button("Download", start_download, disabled=is_downloading)

    if is_downloading:
        Progress("Downloading...")

    solara.Text(status)
