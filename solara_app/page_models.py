from pathlib import Path
import solara

import r2
from solara_app.folders import CHECKPOINTS

from solara_app.mini_components.simple import Progress


@solara.component
def DownloadModels():
    models = solara.use_thread(lambda: r2.list_files("models"))
    selected_models: solara.Reactive[list[str]] = solara.use_reactive([])

    if models.state == solara.ResultState.FINISHED:
        unavailable_models: list[str] = [
            m for m in (models.value or []) if not Path(m).exists()
        ]
        solara.SelectMultiple(
            "Select model(s) to download",
            selected_models,
            unavailable_models,  # type: ignore
        )

        for m in selected_models.value:
            output = solara.use_thread(
                lambda: r2.download(f"models/{m}", out_folder=CHECKPOINTS)
            )
            if output.state == solara.ResultState.RUNNING:
                Progress(f"Downloading {m}...")
            elif output.state == solara.ResultState.FINISHED:
                solara.Success(f"Downloaded {output.value}", icon=True)
