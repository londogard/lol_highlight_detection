import solara
from ipywidgets import Video as iPyVideo

@solara.component()
def Progress(msg: str):
    with solara.Column(align="center", style={"justify-content": "center"}):
        solara.SpinnerSolara()
        solara.Markdown(msg)

@solara.component
def Video(file_name: str, width: int=500, autoplay: bool=False, loop: bool=False):
    vid = iPyVideo.from_file(file_name, width=width, autoplay=autoplay, loop=loop)
    solara.display(vid)
