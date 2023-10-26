from pathlib import Path
import solara
import solara.lab
from solara_app import utils
from solara_app.page_download import DownloadConvertPersist
from solara_app.page_inference import Inference


@solara.component
def DatasetR2():
    twitch_id, set_twitch_id = solara.use_state("")
    is_downloading, set_downloading = solara.use_state(False)
    status, set_status = solara.use_state("")

    solara.Button("Download all data from R2", color="green")


@solara.component
def Page():
    with solara.Sidebar():
        solara.Title("League of Legend Highlight Extractor")
        dump_file = utils.persist_uploaded_file("rclone.conf")
        solara.FileDrop(label="Drop R2 Config", lazy=False, on_file=dump_file)
    if not Path("rclone.conf").exists():
        solara.Error("Upload rclone.conf first!")
    else:
        with solara.lab.Tabs():
            with solara.lab.Tab("Inference"):
                Inference()
            with solara.lab.Tab("Download, Convert and Persist Twitch Clips"):
                DownloadConvertPersist()


Page()
