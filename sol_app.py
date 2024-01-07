from pathlib import Path
import solara
import solara.lab
import r2
from solara_app import folders, sol_utils
from solara_app.mini_components.simple import Progress
from solara_app.page_download import DownloadConvertPersist
from solara_app.page_inference import Inference

PROMPT = """<|system|>
                    You are a chatbot who help write successful titles for Youtube videos of League of Legends Highlights from TheBaus that are generated using AI!</s>
                    <|user|>
                    Write me a title that fits a video of TheBaus who wins games as Sion even through having a lot of deaths - good deaths.</s>
                    <|assistant|>"""


@solara.component
def SidebarUpload():
    with solara.Sidebar():
        solara.Title("League of Legend Highlight Extractor")
        dump_file = sol_utils.persist_uploaded_file("rclone.conf")
        solara.FileDrop(label="Drop R2 Config", lazy=False, on_file=dump_file)


@solara.component
def Page():
    folders.create_default_folders()
    import requests

    # Check if there is a network connection available
    req = requests.get("https://google.com", timeout=2)
    # if req.status_code == 200:
    #    models = solara.use_thread(lambda: r2.list_files("models"))
    #    if models.state == solara.ResultState.FINISHED:
    #        for m in models.value:
    #            solara.use_thread(lambda: r2.download(m, out_folder="ckpts"))

    SidebarUpload()

    if not Path("rclone.conf").exists():
        solara.Error("Upload rclone.conf first!")
    else:
        with solara.lab.Tabs():
            with solara.lab.Tab("Inference"):
                Inference()
            with solara.lab.Tab("Download, Convert and Persist Twitch Clips"):
                DownloadConvertPersist()
            with solara.lab.Tab("Generate Video Title"):
                solara.Markdown(
                    """
                    ## Title Generator

                    Generate a title using a Large Language Model (**LLM**).
                    """
                )
                solara.InputText(
                    "What should title be based on?",
                    "TheBaus is a famous streamer who usually plays Sion, this highlight sections show-cases both (good) deaths and wins!",
                )
                from transformers import pipeline

                title = solara.use_reactive(None)
                clicks = solara.use_reactive(0)

                def gen_title():
                    pipe = pipeline(
                        "text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
                    )
                    out = pipe(PROMPT)
                    title.value = out[0]["generated_text"].replace(PROMPT, "")

                solara.Button(
                    "Generate!", on_click=lambda: clicks.set(clicks.value + 1)
                )

                if clicks.value > 0:
                    res = solara.use_thread(gen_title)
                    if res.state == solara.ResultState.RUNNING:
                        Progress("Running...")
                if title.value:
                    solara.Markdown(f"Title:")
                    solara.Text(title.value)
