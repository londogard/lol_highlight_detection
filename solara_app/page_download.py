import solara
import torch
import ingest
import r2


# elif file["name"].rsplit(".", 1)[1] not in SUPPORTED_FMTS:
#        solara.Error(f"Invalid file type - only {SUPPORTED_FMTS} supported!")
#        file = None
@solara.component()
def DownloadConvertPersist():
    twitch_id, set_twitch_id = solara.use_state("")
    is_downloading, set_downloading = solara.use_state(False)
    status, set_status = solara.use_state("")

    def start_download():
        set_downloading(True)
        set_status("")
        ingest.download_twitch_stream(twitch_id, end_time="00:05:00")
        ingest.vid_to_frames(twitch_id, use_cuda=torch.cuda.is_available())
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
