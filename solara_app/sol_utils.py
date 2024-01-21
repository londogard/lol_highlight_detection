from typing import Callable
from solara.components.file_drop import FileInfo
import solara
import polars as pl
import plotly.express as px

from solara_app.folders import CHECKPOINTS, CONVERTED


def persist_uploaded_file(
    filename: str, key: str = "data"
) -> Callable[[FileInfo], None]:
    def func(data: FileInfo) -> None:
        with open(filename, "wb") as f:
            f.write(data[key])

    return func


@solara.component
def ModelFileSelectComponent(
    file: solara.Reactive[str],
    model: solara.Reactive[str],
    clicked: solara.Reactive[bool],
):
    files = [str(p) for p in CONVERTED.glob("*") if p.is_dir()]
    models = [str(p) for p in CHECKPOINTS.rglob("*.ckpt")]
    _clicked = solara.use_reactive(clicked)
    with solara.Details("Select Video", expand=True):
        solara.Select(
            "Select File",
            values=files,
            value=file,
        )
        solara.Select(
            "Select Model",
            values=models,
            value=model,
        )
        solara.Button(
            "Run Inference!",
            color="primary",
            on_click=lambda: _clicked.set(True),
        )


@solara.component
def CutOffChartSelection(cut_off: solara.Reactive[float], df: pl.DataFrame):
    div = solara.Column()

    solara.SliderInt(
        "Highlight Y-Cutoff",
        cut_off,
        min=df["preds"].min() + 1,
        max=df["preds"].max(),
        thumb_label="always",
        tick_labels="end_points",
    )
    with div:
        fig = px.line(
            df.cast({"timestamp": str}),
            x="timestamp",
            y="preds",
            line_shape="hv",
        )
        fig.add_hline(y=cut_off.value, line_color="red")
        solara.FigurePlotly(fig)
