import solara


@solara.component()
def Progress(msg: str):
    with solara.Column(align="center", style={"justify-content": "center"}):
        solara.SpinnerSolara()
        solara.Markdown(msg)
