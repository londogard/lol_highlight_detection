from pathlib import Path
import solara
import solara.lab
from solara_app import folders, sol_utils
from solara_app.mini_components.simple import Progress
from solara_app.page_download import DownloadConvertPersist
from solara_app.page_inference import Inference
from solara_app.page_models import DownloadModels

PROMPT = """<|system|>
                    You are a chatbot who help write successful titles for Youtube videos of League of Legends Highlights from TheBaus that are generated using AI!</s>
                    <|user|>
                    Write me a title that fits a video of TheBaus who wins games as Sion even through having a lot of deaths - good deaths.</s>
                    <|assistant|>"""


@solara.component
def SidebarUpload(selected_page: solara.Reactive[str]):
    with solara.Sidebar():
        solara.Title("League of Legend Highlight Extractor")
        if Path("rclone.conf").exists():
            solara.Success("rclone.conf uploaded.")
        else:
            dump_file = sol_utils.persist_uploaded_file("rclone.conf")
            solara.FileDrop(label="Drop R2 Config", lazy=False, on_file=dump_file)
            solara.Error("Upload rclone.conf first!")
        solara.Select(
            "Select Page",
            [
                "Inference",
                "Download, Convert and Persist Twitch Clips",
                "Download Model(s)",
                "Generate Video Title",
            ],
            value=selected_page,
        )


@solara.component
def Page():
    folders.create_default_folders()

    selected_page = solara.use_reactive("Inference")
    SidebarUpload(selected_page)

    if not Path("rclone.conf").exists():
        solara.Error("Upload rclone.conf first!")
    else:
        if selected_page.value == "Inference":
            Inference()
        elif selected_page.value == "Download, Convert and Persist Twitch Clips":
            DownloadConvertPersist()
        elif selected_page.value == "Download Model(s)":
            DownloadModels()
        elif selected_page.value == "Generate Video Title":
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

            solara.Button("Generate!", on_click=lambda: clicks.set(clicks.value + 1))

            if clicks.value > 0:
                res = solara.use_thread(gen_title)
                if res.state == solara.ResultState.RUNNING:
                    Progress("Running...")
            if title.value:
                solara.Markdown("Title:")
                solara.Text(title.value)
