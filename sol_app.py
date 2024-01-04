from pathlib import Path
import solara
import solara.lab
import r2
from solara_app import folders, sol_utils
from solara_app.page_download import DownloadConvertPersist
from solara_app.page_inference import Inference


@solara.component
def Page():
    folders.create_default_folders()
    models = r2.list_files("models")
    for m in models:
        r2.download(m)

    with solara.Sidebar():
        solara.Title("League of Legend Highlight Extractor")
        dump_file = sol_utils.persist_uploaded_file("rclone.conf")
        solara.FileDrop(label="Drop R2 Config", lazy=False, on_file=dump_file)
    if not Path("rclone.conf").exists():
        solara.Error("Upload rclone.conf first!")
    else:
        with solara.lab.Tabs():
            with solara.lab.Tab("Inference"):
                Inference()
            with solara.lab.Tab("Download, Convert and Persist Twitch Clips"):
                DownloadConvertPersist()
