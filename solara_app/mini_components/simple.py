from typing import Any
import solara
from ipywidgets import Video as iPyVideo


@solara.component()
def Progress(msg: str):
    with solara.Column(align="center", style={"justify-content": "center"}):
        solara.SpinnerSolara()
        solara.Markdown(msg)


@solara.component()
def ProgressDynamic(
    msg: str,
    result: solara.Result[Any],
    dynamic_progress: solara.Reactive[str | int | float] | None = None,
):
    if result.state == solara.ResultState.RUNNING:
        Progress(msg)
        if dynamic_progress is not None:
            progress = dynamic_progress.value
            match progress:
                case int():
                    solara.ProgressLinear(progress)
                case float():
                    solara.ProgressLinear(int(progress * 100))
                case str():
                    solara.Markdown(progress)


@solara.component
def Video(file_name: str, width: int = 500, autoplay: bool = False, loop: bool = False):
    vid = iPyVideo.from_file(file_name, width=width, autoplay=autoplay, loop=loop)
    solara.display(vid)
